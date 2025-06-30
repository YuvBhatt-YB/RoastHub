
import requests
import json
import os
from openai import OpenAI

token = os.environ.get("token")
openrouter_token=os.environ.get("openrouter_token")
base_url = "https://api.github.com"
headers = {
    'Accept': 'application/vnd.github+json',
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {token}"
    }

def get_username(username):
    user_stats = {}
    prompt_one = ""
    url = f"{base_url}/users/{username}"
    response = requests.get(url,headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    user_stats["name"] = data["login"]
    user_stats["bio"] = data["bio"]
    user_stats["profilePic"] = data["avatar_url"]
    user_stats["totalRepos"] = data["public_repos"]
    prompt_one = f"""This is the GitHub profile of user `{user_stats["name"]}`.\n- Bio: {user_stats["bio"]}\n- Total Public Repos: {user_stats["totalRepos"]}\n"""
    return {"user_stats":user_stats,"prompt_one":prompt_one}

def score_repo(repo):
    stars = repo["stargazers_count"]
    desc = repo["description"] or ""
    tutorialKeywords = ["tutorial","clone","bootcamp","assignment","course"]
    is_tutorial = any(kw in desc.lower() for kw in tutorialKeywords)

    score = (stars*10) + len(desc) + (0 if is_tutorial else 100)
    return score

def get_repos_stats(username):
    prompt_two = """- Top Notable Projects:\n"""
    url = f"{base_url}/users/{username}/repos?per_page=100"
    response = requests.get(url,headers=headers)
    data = response.json()
    repos = []
    if not data:
        prompt_two = "No projects in Github"
        return {"repos":repos,"prompt_two":prompt_two}
    for r in data:
        r["score"] = score_repo(r)
    sorted_repos = sorted(data,key = lambda y:y["score"],reverse=True)[:10]
    for repo in sorted_repos:
        r = {
            "name":repo["name"],
            "description":repo["description"],
            "stars":repo["stargazers_count"],
            "score":repo["score"],
            "updated_at":repo["updated_at"]
            }
        repos.append(r)
        prompt_two += f"- {r["name"]} ({r["stars"]} stars) – {r["description"]}\n"
    return {"repos":repos,"prompt_two":prompt_two}

def build_prompt(prompt_1,prompt_2):
    remaining = """\nNow:\n1. Give a github account rating out of 10\n2. Roast it in a witty way\n3. Point out good things\n4. Point out what’s missing or bad\n5. Write a “recruiter’s impression” in 1 sentence\nGive all answer in json format\nMake sure the json keys are as follows:"rating" github rating,"roast" actual roast,"good_things" which is a list of good things ,"missing_or_bad" which is a list of bad things,"recruiter_impression"\nmake sure to strictly follow the format"""
    result_prompt = prompt_1 + prompt_2 + remaining
    return result_prompt

def call_openrouter_llm(prompt):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=f"{openrouter_token}",
    )
    try:
        completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>", 
        },
        extra_body={},
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        messages=[
        {
            "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": f"{prompt}"
                },
            ]
        }
        ]
        )
        final_message = (completion.choices[0].message.content).replace("```","").replace("json","")
    
        return json.loads(final_message)
    
    except json.JSONDecodeError as e:
        print("JSON decode error",e)
        return {"error":"Failed to parse response.Please try again"}
    
    except Exception as e:
        print("Openrouter call failed",e)
        return {"error":"Something went wrong while roasting you.Please try again"}