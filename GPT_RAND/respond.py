import importlib, urllib.request, json, ssl

import importlib
import urllib.request
import json
import ssl

from tenacity import (
    retry,
    stop_after_attempt,  # Added for limiting retry attempts
    wait_exponential,  # Changed from wait_fixed to wait_exponential
    wait_fixed
)

gpt_250 = 'fd141762ad904a91b170781fcb428b04'  # GPT-4 enabled

def endUrl(deployment, api,
           base='https://apigw.rand.org/openai/RAND/inference/deployments/', 
           method='/chat/completions?api-version='):
    return base + deployment + method + api

def sendRequest(url, hdr, data):
    data = json.dumps(data)
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=hdr, data=bytes(data.encode("utf-8")))
    req.get_method = lambda: 'POST'
    
    try:
        response = urllib.request.urlopen(req, context=context, timeout=10)  # Added timeout
        content = bytes.decode(response.read(), 'utf-8')  # Return string value
        return json.loads(content)
    except urllib.error.URLError as e:  # Added specific error handling
        print(f"Network error: {e}")
        raise
    except Exception as e:  # General exception handling
        print(f"Unexpected error: {e}")
        raise

@retry(wait=wait_exponential(multiplier=1, min=2, max=7))#, stop=stop_after_attempt(5))  # Modified retry logic
def Respond(prompt, context='', t=1, c=1, GPT='4om', n=1, print_rslt=False):
    '''Makes text calls to RAND's internal GPT'''

    key = gpt_250
    try:
        api = '2024-06-01'  # Updated 10/15/24
        
        Deployment = {
            '3': 'gpt-35-turbo-v0125-base',
            '4': 'gpt-4-v0613-base',
            '4o': 'gpt-4o-2024-08-06',
            '4om': 'gpt-4o-mini-2024-07-18',
        }
    
        Model = {
            '3': 'gpt-35-turbo',
            '4': 'gpt-4',
            '4o': 'gpt-4o',
            '4om': 'gpt-4o-mini',
        }
        
        deployment = Deployment[GPT]
        model = Model[GPT]
        
        url = endUrl(deployment, api)
        
        hdr = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': key,
        }
        
        data = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': context},
                {'role': 'user', 'content': prompt}],
            'temperature': t,
            'top_p': c,
            'n': n,
        }
        
        res = sendRequest(url, hdr, data)
        
        Results = [res['choices'][i]['message']['content'] for i in range(n)]
        if print_rslt:
            for answer in Results:
                print('#---------------------------------#')
                print(answer)
        return Results
    except Exception as e:
        print(e)
        raise

@retry(wait=wait_fixed(2))
def Summarize(text, context = '',T = .3, C = 1, N = 1, print_rslt = False, GPT = '4om'): 
    
    context0 = 'You are a helpful assistent that carefully and completely: reads, thinks through, and executes tasks.'
    #descriptions #triple
    if context == '':
        context = 'For the following summarize this into one very short paragraph highlighting important ideas.'
    
    request =  context
    prompt = text

    answer = Respond(request + '\n' + prompt, context = context0, t = T, c = C, GPT = GPT, n = N)
    
    if print_rslt == True:
        for a in answer:
            print(a)
            print('#############')

    return answer




# def Cluster(idz, dscrps, T = 2, C = .7, N = 1,ret = False, GPT = '4om'):
#     print('#############')
#     #Turn down c when vaiance of answers goes up
#     instruct = 'First, for the following descriptions, delimited by triple backticks, summarize these using one complete sentence by highlighting only common themes and terms, but do not create a list. Second, add a list of common terms.'
#     answer = Summarize((dscrps[idz]).to_list(),
#                           context = instruct, T = T, C = C, N = N, ret = ret, GPT = GPT)
#     for i in idz:
#         print('------------')
#         print(dscrps[i])
#     if ret == True:
#         return answer


# @retry(wait=wait_fixed(2))
# def Title(item, context = '',T = .3, C = 1, N = 1, ret = False, GPT = '4om'): 
    
#     context0 = 'You are a helpful assistent that carefully and completely: reads, thinks through, and executes tasks.'
#     #descriptions #triple
#     if context == '':
#         context = """\
#         You will be provided with a summary of documents that came from the same cluster. \
#         The summary will be delimited with triple backticks. \
#         Your task is to define a topic title that likley and uniquley represents the summary of the documents.\
#         Do not include the word "Title:" at the beggining of your response.
#         """
    
#     text  = '```'+ item +'```'
    
#     request =  context
#     prompt = text

#     answer = Respond(request + '\n' + prompt, context = context0, t = T, c = C, GPT = 4, n = N)
    
#     if ret == True:
#         return answer
#     else:
#         for a in answer:
#             print(a)
#             print('#############')


# @retry(wait=wait_fixed(2))
# def Label(item, context = '',T = .3, C = 1, N = 1, ret = False, GPT = '4om'): 
    
#     context0 = 'You are a helpful assistent that carefully and completely: reads, thinks through, and executes tasks.'
#     #descriptions #triple
#     if context == '':
#         context = """\
#         You will be provided with a title of a set of documents . \
#         The title will be delimited with triple backticks. \
#         Your task is to come up with a 1 to 3 word label that generally but uniquley represents the title of the documents.\
#         Do not include the word "Label:" at the beggining of your response.
#         """
    
#     text  = '```'+ item +'```'
    
#     request =  context
#     prompt = text

#     answer = Respond(request + '\n' + prompt, context = context0, t = T, c = C, GPT = GPT, n = N)
    
#     if ret == True:
#         return answer
#     else:
#         for a in answer:
#             print(a)
#             print('#############')       
# # txt = '''
# # '''
# # ctxt = "How do I color my first dataframe, df, based on the values of a different dataframe, df2, of the same size?'"

# # answers = gptRespond(txt, ctxt, t = 1, c = 1, GPT = '4', n = 2)
# # for answer in answers:
# #     print(answer)