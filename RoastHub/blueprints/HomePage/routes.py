from flask import Blueprint,render_template,request
from RoastHub.blueprints.HomePage.functions import get_username,get_repos_stats,build_prompt,call_openrouter_llm
HomePage = Blueprint("HomePage",__name__,template_folder="templates")

@HomePage.route("/")
def index():
    return render_template("HomePage/index.html")


@HomePage.route("/analyze",methods=["POST"])
def analyze():
    username = request.form["username"]

    user_resp = get_username(username)
    if user_resp is None:
        return render_template("Homepage/user_not_found.html")
    
    repos_resp = get_repos_stats(username)
    
    prompt = build_prompt(user_resp["prompt_one"],repos_resp["prompt_two"])

    roast_response = call_openrouter_llm(prompt)
    if "error" in roast_response:
        return render_template("Homepage/error.html",message=roast_response["error"])
    
    
    return render_template("HomePage/result.html",username=username,user_resp=user_resp,user_data=user_resp["user_stats"],repos = repos_resp["repos"],roast=roast_response)