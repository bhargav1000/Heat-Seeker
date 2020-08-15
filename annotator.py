import pandas as pd

def dataset_annotation(dataset):
    import re
    from dateparser.search import search_dates
    output_data=[]
    for index, row in dataset.iterrows():
        accountid_string=''
        amount_string=''
        balance_string=''
        found_date=''
        accountid_string_start=0
        accountid_string_end=0
        amount_string_start=0
        amount_string_end=0
        balance_string_start=0
        balance_string_end=0
        
        msg=row['msg'].lower() # always convert message to lowercase
        msg = msg.replace(",", "")
        msg = msg.replace(".", " ") # remove this line if not working
        doc=nlp(msg)
        wordlist=[msg.text for msg in doc] # list of words from message
        wordlist2=msg.split(' ')

        # account_id info
        accountid_present=None
        if pd.isna(row['accountid']):
            accountid_present=False
            accountid_entity=('empty')
        else:
            accountid=row['accountid'][-4:] # select only last 4 characters from accountid
            try:
                accountid_list = [i for i in wordlist if accountid in i] # gets list of substrings with matches
                accountid_string=accountid_list[0] # take first instance from res
                accountid_string_start=msg.find(accountid_string)
                accountid_string_end=accountid_string_start+len(accountid_string)
                accountid_entity=(accountid_string_start, accountid_string_end, 'Account')
                accountid_present=True
            except IndexError:
                accountid_present=False
                accountid_entity=('empty')

        # amount info
        amount_present=None
        if pd.isna(row['amount']):
            amount_present=False
            amount_entity=('empty')
        else:
            amount=str(int(row['amount']))
            try:
                amount_list = [i for i in wordlist if amount in i] # gets list of substrings with matches
                amount_string=amount_list[0]
                amount_string=re.findall(r'-?\d+\.?\d*', amount_string)[0]
                amount_string_start=msg.find(amount_string)
                amount_string_end=amount_string_start+len(amount_string)
                amount_entity=(amount_string_start, amount_string_end, 'Amount')
                amount_present=True
            except IndexError:
                amount_present=False
                amount_entity=('empty')
        
        # balance info
        balance_present=None
        if pd.isna(row['balance']):
            balance_present=False
            balance_entity=('empty')
        else:
            balance=str(int(row['balance']))
            try:
                balance_list = [i for i in wordlist if balance in i] # gets list of substrings with matches
                balance_string=balance_list[0]
                balance_string=re.findall(r'-?\d+\.?\d*', balance_string)[0]
                balance_string_start=msg.find(balance_string)
                balance_string_end=balance_string_start+len(balance_string)
                balance_entity=(balance_string_start, balance_string_end, 'Balance')
                balance_present=True
            except IndexError:
                balance_present=False
                balance_entity=('empty')
            
        # building entity dictionary
        entity_dict={}
        entity_list=[]
        # check presence
        entity_presence=[accountid_present, amount_present, balance_present]
        
        entity_list=[accountid_entity, amount_entity, balance_entity]
        
        entity_present=[item for item, condition in zip(entity_list, entity_presence) if condition]
        entity_dict['entities']=entity_present
        output=(msg, entity_dict)
        #print(output)
        output_data.append(output)
    return output_data
