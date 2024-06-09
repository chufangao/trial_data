import json
import os
import glob
import re
import pandas as pd
from tqdm import tqdm
import argparse


def main(gpt_decisions_path,top_2_pubmed_path):
    # get list of .json files in gpt_decisions_path
    json_files = glob.glob(os.path.join(gpt_decisions_path, '*.json'))
    
    # get top 2 pubmed abstracts used
    top2_pubmed_pd = pd.read_csv(top_2_pubmed_path)
    
    # for each trial in the pubmed pd, extract trial outcome from json file
    # concat trial outcome to pubmed pd
    # save to new csv   
    # create a new dataframe with trial nct ids and outcomes
    gpt_trial_outcomes = pd.DataFrame(columns=['nct_id', 'outcome'])
    
    for trial in tqdm(top2_pubmed_pd['nct_id'].values):
        # print(trial)
        if os.path.exists(os.path.join(gpt_decisions_path,f'{trial}_gpt_response.json')):
            with open(os.path.join(gpt_decisions_path,f'{trial}_gpt_response.json'), 'r') as f:
                json_data = json.load(f)
                f.close()
            
            # extract trial outcome
            trial_outcome = json_data['outcome']
            
            # add to gpt_trial_outcomes using concat
            gpt_trial_outcomes = pd.concat([gpt_trial_outcomes, pd.DataFrame({'nct_id': [trial], 'outcome': [trial_outcome]})])
            


    # merge top2_pubmed_pd with gpt_trial_outcomes on nct_id 
    merged_pd = pd.merge(top2_pubmed_pd,gpt_trial_outcomes,  on='nct_id', how='left')
    merged_pd.dropna(subset=['top_1_similar_article_title'], inplace=True)
    # rename background column to num_of_background_pubs, similar for derived and result
    merged_pd.rename(columns={'background': 'num_of_background_pubs', 'derived': 'num_of_derived_pubs', 'result': 'num_of_result_pubs','nct_id':'nctid'}, inplace=True)

    print(f'Number of trials with outcomes: {len(merged_pd)}')
    
    # save csv file
    merged_pd['outcome'] = merged_pd['outcome'].map({'unsure': 'Not sure', 'Unsure': 'Not sure', 'success': 'Success', 'Success': 'Success', 'partial success': 'Success', 'Fail': 'Failure', 'fail': 'Failure', 'failure': 'Failure'})
    save_path = top_2_pubmed_path.replace('top_2_extracted_pubmed_articles.csv','')
    merged_pd.to_csv(os.path.join(save_path,'pubmed_gpt_outcomes.csv'), index=False)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpt_decisions_path', type=str, default= None, help='Path to the folder with gpt decisions')
    parser.add_argument('--top_2_pubmed_path', type=str, default= None, help='Path to the dataframe with top 2 extracted pubmed articles')
    args = parser.parse_args()
    if args.gpt_decisions_path is None:
        raise ValueError('Please provide the path to the folder with gpt decisions')    
    if args.top_2_pubmed_path is None:
        raise ValueError('Please provide the path to the dataframe with top 2 extracted pubmed articles')
    
    
    main(args.gpt_decisions_path,args.top_2_pubmed_path)
    print(f'Final outcomes saved in {args.top_2_pubmed_path.replace("top_2_extracted_pubmed_articles.csv","")}pubmed_gpt_outcomes.csv')
    print('Done')
    
    
# python clean_and_extract_final_outcomes.py --gpt_decisions_path '/home/jp65/Clinical_Trials/test_pubmed_extract/gpt_35' --top_2_pubmed_path '/home/jp65/Clinical_Trials/test_pubmed_extract/top_2_extracted_pubmed_articles.csv'