#include <iostream>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <string>
#include <sstream>
#include <unordered_map>
#include <bits/stdc++.h>
 
#include <archive.h>
#include <archive_entry.h>
#include "utils/feature_writer.h"
#include "utils/text_utils.h"
#include "utils/utils.h"
#include "dataset.h"
#include "features.h"
#include "utils/feature_parser.h"
#include "utils/simple-cmd-line-helper.h"

using namespace std;
 
string get_tempfile(){
    char file_template [] = "/tmp/CAL_XXXXXX";
    mkstemp(file_template);
    return file_template;
}

inline void ltrim_(string &str) {
    str.erase(str.begin(), find_if(str.begin(), str.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

inline void rtrim_(string &str) {
    str.erase(find_if(str.rbegin(), str.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), str.end());
}

inline void trim(string &str){
    str.erase( std::remove(str.begin(), str.end(), '\r'), str.end() );
    ltrim_(str);
    rtrim_(str);
}
/**
 *  Extract paragraphs from documents.
 */
vector<string> get_paragraphs(const string& document) {
    vector<string> paragraphs;
    istringstream stream(document);
    string paragraph;

    // Split paragraphs by \n\n
    while (getline(stream, paragraph, '\n')) {
        if (paragraph.empty()) {
            paragraphs.push_back("");
        } else {
            paragraphs.back() += paragraph + "\n";
        }
    }

    vector<string> final_paragraphs;
    vector<string> cur_para;
    for (const auto& para : paragraphs) {
        string trimmed_para = para;
        trim(trimmed_para);
        if (trimmed_para.empty()) {
            continue;
        }

        if (accumulate(cur_para.begin(), cur_para.end(), string()).length() <= 100) {
            cur_para.push_back(trimmed_para);
        } else {
            final_paragraphs.push_back(accumulate(cur_para.begin(), cur_para.end(), string("\n\n")));
            cur_para = {trimmed_para};
        }
    }
 
    if (!cur_para.empty() && accumulate(cur_para.begin(), cur_para.end(), string()).length() < 100 && !final_paragraphs.empty()) {
        final_paragraphs.back() += "\n\n" + accumulate(cur_para.begin(), cur_para.end(), string("\n\n"));
    } else if (!cur_para.empty()) {
        final_paragraphs.push_back(accumulate(cur_para.begin(), cur_para.end(), string("\n\n")));
    }
    return final_paragraphs;
}
 
unordered_map <string, string> process_documents(const vector<string> &documents){
    unordered_map<string, string> paragraphs;
    for (auto i=0; i<documents.size(); i++){
        vector<string> paragraphs_per_doc = get_paragraphs(documents[i]);
        // Save each paragraph title with the format (doc_id).(para_id)
        for(auto j=0; j< paragraphs_per_doc.size(); j++){
            paragraphs[to_string(i)+"."+to_string(j)] = paragraphs_per_doc[j];
        }
    }
    return paragraphs;
}
 
void parse_documents(const vector<string>& documents, const string &out_filename, const string &para_out_filename){
    string pass1_filename = get_tempfile();
    unordered_map<string, uint32_t> token_ids;
    vector<double> idf(1);
    vector<pair<string, uint32_t>> dictionary;
    size_t num_docs = 0;
    size_t doc_id = 1;
 
    BMITokenizer tokenizer = BMITokenizer();
    // Pass 1: get corpus stat and compute term frequencies
    {
        unique_ptr<FeatureWriter> fw_1;
        fw_1 = make_unique<BinFeatureWriter>(pass1_filename, vector<pair<string, uint32_t>>());
 
        for (const string & document:documents){
            num_docs++;
            doc_id++;
            vector<string> tokens = tokenizer.tokenize(document);
 
            vector<FeatureValuePair> features;
            for (pair<string, int> token: features::get_tf(tokens)) {
                if (token_ids.count(token.first) == 0) {
                    dictionary.push_back({token.first, 0});
                    token_ids[token.first] = dictionary.size();
                }
                dictionary[token_ids[token.first]-1].second += 1.0;
                features.push_back({token_ids[token.first], (float) token.second});
            }
 
            sort(features.begin(), features.end(),
                 [](const FeatureValuePair &a, const FeatureValuePair &b) -> bool { return a.id_ < b.id_; });
 
            fw_1->write(SfSparseVector(to_string(num_docs), features));
            cerr<<num_docs<<" documents processed\r";
        }
        fw_1->finish();
    }
    cerr<<endl<<"Computing idf"<<endl;
 
    vector<int> new_ids(dictionary.size());
    for(int i = 0; i < dictionary.size(); i++){
        new_ids[i] = i;
    }
    // Compute idf
    {
        int end = dictionary.size() - 1;
        for(int i = 0; i <= end; i++){
            if(dictionary[i].second < 2){
                while(end > i){
                    if(dictionary[end].second > 1){
                        swap(dictionary[i], dictionary[end]);
                        new_ids[i] = end;
                        new_ids[end] = i;
                        break;
                    }
                    end--;
                }
            }
            idf.push_back(dictionary[i].second < 2?-1:log(num_docs / (float)dictionary[i].second));
        }
        while(dictionary[end].second < 2)
            end--;
        dictionary = vector<pair<string, uint32_t>>(dictionary.begin(), dictionary.begin() + end + 1);
    }
    cerr<<"Beginning Pass 2"<<endl;
    // Pass 2
    unique_ptr<FeatureParser> fp_1;
    unique_ptr<FeatureWriter> fw_2;

    fp_1 = make_unique<BinFeatureParser>(pass1_filename);
    fw_2 = make_unique<BinFeatureWriter>(out_filename, dictionary);
 
    unique_ptr<SfSparseVector> spv;
    unordered_map<uint32_t, string> id_tokens;
 
    num_docs = 0;
    while((spv = fp_1->next()) != nullptr){
        vector<FeatureValuePair> features;
        double sum = 0;
        for(auto &f: spv->features_){
            if(f.id_ != 0){
                f.id_ = new_ids[f.id_-1] + 1;
                if(f.id_ - 1 < dictionary.size() && dictionary[f.id_-1].second > 1){
                    features.push_back({f.id_, (float) ((1 + log(f.value_)) * idf[f.id_])});
                    id_tokens[f.id_] = dictionary[f.id_-1].first;
                    sum += features.back().value_ * features.back().value_;
                }
            }
        }
 
        sum = sqrt(sum);
 
        for(auto &f: features){
            f.value_ /= sum;
        }
 
        sort(features.begin(), features.end(),
             [](const FeatureValuePair &a, const FeatureValuePair &b) -> bool { return a.id_ < b.id_; });
 
        fw_2->write(SfSparseVector(spv->doc_id, features));
        num_docs++;
        cerr<<num_docs<<" documents processed\r"<<endl;
    }
    cerr<<endl;
    fw_2->finish();
 
    cerr<<"Generating Paragraph features"<<endl;
    unordered_map<string, string> paragraphs = process_documents(documents);
 
    unique_ptr<FeatureWriter> para_fw;
 
    para_fw = make_unique<BinFeatureWriter>(para_out_filename, dictionary);
 
    for (auto it=paragraphs.begin(); it != paragraphs.end(); it++) {
        string para_name = it->first, paragraph = it->second;
        // cout << para_name<<": "<<paragraph.size()<<":"<<paragraph<<endl;
        num_docs++;
        vector<string> tokens = tokenizer.tokenize(paragraph);
 
        vector<FeatureValuePair> features;
        double sum = 0;
        for (pair<string, int> token: features::get_tf(tokens)) {
            if (token_ids.count(token.first) == 0) {
                continue;
            }
            uint32_t id = new_ids[token_ids[token.first]-1] + 1;
            if(id - 1 < dictionary.size() && dictionary[id-1].second > 1){
                float wt = (float) (token.second * idf[id]);
                features.push_back({id, wt});
                sum += wt * wt;
            }
        }
        sum = max(20.0, sqrt(sum));
        for(auto &f: features){
            f.value_ /= sum;
        }
 
        sort(features.begin(), features.end(),
             [](const FeatureValuePair &a, const FeatureValuePair &b) -> bool { return a.id_ < b.id_; });
 
        para_fw->write(SfSparseVector(para_name, features));
        cerr<<num_docs<<" paragraphs processed\r";

    }
    para_fw->finish();
}
 
// int main(){
//     string out_filename = "data/kouki_sample.bin", out_para_filename = "data/kouki_para_sample.bin", doc;
//     doc = R"(
//    From:	Jeb Bush
//     Sent:	Wednesday, January 1, 2003 5:16 PM
//     To:	'DORANB36@aol.com'
//     Subject:	RE: DCF Placed Children In Care Of Ex-Convicts

//     Happy New Year.
    

//     Jeb Bush

//     ***********************************************************
//     Please note: Florida has a very broad public records law.
//     Most written communications to or from state officials
//     regarding state business are public records available to the
//     public and media upon request. Your e-mail communications
//     may therefore be subject to public disclosure. 

//     -----Original Message-----
//     From: DORANB36@aol.com [mailto:DORANB36@aol.com]
//     Sent: Wednesday, January 01, 2003 3:44 PM
//     To: Jeb Bush
//     Subject: DCF Placed Children In Care Of Ex-Convicts


//     "The state has placed foster children in the homes of convicted felons, including former drug dealers and armed robbers..........Department of Children and Families knew about their past convictions but allowed them to care for foster children because they had paid for their crimes and reformed their behavior."
//     COMMENT: I think you need to take another cruise to somewhere, anywhere and make it a one-way trip.
//     =============================================================
//     DCF Placed Children In Care Of Ex-Convicts
//     The Associated Press 
//     Published: Jan 1, 2003

//     MIAMI - The state has placed foster children in the homes of convicted felons, including former drug dealers and armed robbers, according to a newspaper report Tuesday. One Miami man convicted of child endangerment in New York for allegedly raping a child pleaded guilty later to raping a foster child in his care in Florida, according to an investigation by The Miami Herald. 

//     Another foster parent pleaded guilty to armed robbery for breaking into a man's apartment and holding him at gunpoint with her boyfriend in 1988. And a Jacksonville man who served 15 years in prison for heroin trafficking became a foster parent along with his wife in July. 



//     Felons Say Agency Aware Of Records 

//     Foster parents contacted by the newspaper said the Department of Children and Families knew about their past convictions but allowed them to care for foster children because they had paid for their crimes and reformed their behavior. 

//     ``They know everything about me,'' said Leon Campbell, who was released from prison in 1991 after serving time for heroin trafficking. He now helps run his local church and is involved with a prison drug- rehabilitation program. 

//     ``I showed them how my life has changed. Everything was done properly.'' 

//     State law disqualifies people who have been convicted of certain crimes from becoming foster parents, but not all felonies are included on the list of disqualifying offenses. 

//     Not included are welfare fraud, forgery and grand theft. 

//     The state also has discretion to consider how a person has reformed himself or herself in cases in which the applicant's criminal record is more than three years old. 

//     If the person is disqualified, he or she can appeal the decision. 

//     The Herald reported that the state placed foster children in the homes of 168 convicted felons in the last five years and received payments of $10 to $50 a day per child. 

//     There are about 5,000 foster homes in the state. 



//     Internal Investigation Under Way 

//     But DCF officials dispute the number of convicted felons serving as foster parents. 

//     ``Our findings lead us to believe that there are some inaccuracies in the article,'' agency spokesman Bob Brooks said. 

//     ``I don't believe the picture is as bad as it's made out to be.'' 

//     Brooks said he will know how many felons are foster parents next week, when the agency's internal investigation is complete. 

//     Some of the cases revealed by the Herald include: 

//     * Carlos Estrella, convicted of child endangerment for allegedly raping a child in New York in 1966. He became a Florida foster parent in 1995 and received payments from DCF until three days before his 1999 arrest for raping a child in his care. Estrella has since died. DCF is being sued in this case. 

//     * Mary Helen Walley, 52, was sentenced to two years in prison for selling crack cocaine to a Tampa police officer in 1990. She has six foster children. 

//     ``If they didn't think I have what it takes to take care of these children, they wouldn't have given them to me,'' Walley said. 

//     * Ann Ruth Hodges, 33, was sentenced to three years' probation for a home-invasion robbery nearly 15 years ago. 

//     She pleaded guilty to armed robbery, armed burglary, false imprisonment and possession of a firearm during a felony. 

//     The Homestead woman has five foster children. 

//     ``I don't have anything to hide,'' she said. ``I have those crimes in my background, and I'd rather not talk about it.''





//     )";
//     vector <string> docs;
//     docs.push_back(doc);
//     parse_documents(docs, out_filename, out_para_filename);
//     FCGX_Request req = {};
//     vector<pair<string, string>> params;
//     params.emplace_back(make_pair("doc_features", out_filename)),
//     params.emplace_back(make_pair("para_features", out_para_filename));
//     //     make_pair("delimiter", "$$$"),
//     //     make_pair("doc_features", out_filename),
//     //     make_pair("para_features", out_para_filename),
//     // };
//     setup_view(req, params);
// }