# gathera


### Installation
#### Requirements
The system is dockerized into different docker images. Make sure your machine has these installed

* `docker`: Refer to this [installation guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) if you would like to install it on Ubuntu 16.04
* `docker-compose`

#### Corpus and How to Install
Before you start installing, you need to make sure your corpus is ready and in the right format. This step is necessary to be able run the system. We will work with a toy corpus called `athome`.

```
# Clone the repo
git clone https://github.com/UWaterlooIR/gathera.git
cd gathera
# Checkout the sample dataset
git clone https://github.com/hical/sample-dataset.git
cd sample-dataset
python process.py athome4_sample.tgz
# Move files to the data directory which will be mounted to the docker containers
cp athome4_sample.tgz athome4_sample_para.tgz ../data/
cd ..
```

`process.py` is an example of how one might clean the corpus and generate excerpts.
 We will use the `athome4_sample.tgz` and the newly generated `athome4_sample_para.tgz` to generate document features.


```
# Build and access the shell from the cal container
docker-compose run cal bash
root@container-id:/# cd src && make corpus_parser
# Generate features
root@container-id:/# ./corpus_parser  --in /data/athome4_sample.tgz --out /data/athome4_sample.bin --para-in /data/athome4_sample_para.tgz --para-out /data/athome4_para_sample.bin
# Exit the shell with Ctrl+D
```

We will now copy the search index and generate the document and paragraph files which will be showed to the assessors

```
# Extract the tgz files
cd data
# Fetch the anserini index for this collection
wget https://git.uwaterloo.ca/m2abuals/indexes/-/raw/master/athome_sample_index.tar.gz
# Double check MD5 checksum is equal to 59830814de4f1a2363e4dc8242049756
md5 athome_sample_index.tar.gz
# untar index
tar xvzf athome_sample_index.tar.gz

tar xvzf athome4_sample.tgz
mv athome4_test docs
tar xvzf athome4_sample_para.tgz
mv athome4_test para
cd ..

# We are all set! Lets fire up the containers
DOC_BIN=/data/athome4_sample.bin PARA_BIN=/data/athome4_para_sample.bin docker-compose up -d
# Visit localhost:9000
```

If you get a `502 Bad Gateway` error, please wait few seconds while the containers finish processing.

Port `9001` and `9000` will be used by system. Make sure these ports are not being used by other applications in your machine. If you would like to change these ports, please read the configuration section below.

#### How to run
Once your docker images are up and running (you can verify by running docker-compose ps), 
open your browser to [http://localhost:9000/](http://localhost:9000/). 
You should be able to access system's web interface. 
If you are still unable to view the web interface, 
try replacing [http://localhost:9000/](http://localhost:9000/) with the ip address 
of your docker machine (you can get the ip by running docker-machine ip)


#### Working with LATIMES, from TREC Collection
We will now work into adding LATIMES and making it work in GATHERA. First ensure that you have anserini installed and ready to work.
If not, you can clone it from [UWaterloo answerini](https://github.com/UWaterlooIR/anserini).

Once anserini is installed and ready go ahead and create index for latimes.

Inorder to first create the index, we first have to create a new directory called 'latimes'. Inside this directory, we will place our latimes.gz file. Once its done, run the following command:

```
sh target/appassembler/bin/IndexCollection -collection TrecCollection -generator DefaultLuceneDocumentGenerator -threads 1 -input latimes -index indexes/latimes-lucene-index -storePositions -storeDocvectors -storeContents -storeRaw -optimize -compress.path compressed/latimes
```

This will create a directory containing compressed latimes and will also create an index. 

```
# Move compressed files and index to the data directory which will be mounted to the docker containers
cp <compressed-latimes-file-generated> <data-directory-gathera>

# e.g.

cp compressed/latimes.tar.gz ../gathera/data

# Move the generated index to the data directory

cp -r <latimes-lucene-index-directory> <data-directory-gathera>

e.g.
cp -r indexes/latimes-lucene-index ../gathera/data
```

We will now move to gathera directory and set up a few other things before running.

```
# Build and access the shell from the cal container
docker-compose run cal bash
root@container-id:/# cd src && make corpus_parser
# Generate features
root@container-id:/# ./corpus_parser  --in /data/latimes.tar.gz --out /data/latimes.bin --para-in /data/latimes.tar.gz --para-out /data/latimes_para.bin
# Exit the shell with Ctrl+D
```

We are almost done. Now we have to open docker-compose.yml file and point index to the right directory. To do this open the file and change ANSERINI_INDEXI_PATH environment of search to the path where generated index is stored.

```
ANSERINI_INDEXI_PATH=/data/latimes-lucene-index/
```

Now lets make the final changes and start-up gathera.

```
# Uncompress the index files:
cd data
cp latimes.tar.gz docs
cd docs
tar xvzf latimes.tar.gz
cd ..

cp latimes.tar.gz para
cd para
tar xvzf latimes.tar.gz
cd ..

# We are all set! Lets fire up the containers
DOC_BIN=/data/latimes.bin PARA_BIN=/data/latimes_para.bin docker-compose up -d
# Visit localhost:9000
```