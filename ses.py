import sys
from github import Github, GithubException
import pandas as pd
from datetime import datetime, timedelta, date,timezone
import ses
from dateutil.parser import parse

COMMITS_CREATED_BEFORE_DAYS = 100 # No.of days from which commits to be deleted
TAGS_CREATED_BEFORE_DAYS = 100 # No.of days from whicg tags to be deleted
DATE_FORMAT = '%Y-%m-%d'
current_date = str(date.today())
repository_list = []
branch_list = []
author_name_list = []
tag_list =[]
Failed_repos_list = []
Failed_branch_list = []
Failed_auth_name = []
Error = []

# This function is used to get the last commit of a repo head(default) branch
# def get_last_commit_id(repo):
#     commits_from_date = datetime.now() - timedelta(days=COMMITS_CREATED_BEFORE_DAYS)
#     commits = repo.get_commits(since=commits_from_date)
#     last_commit = commits[0]
#     commit_id = last_commit.sha
#     return commit_id

# This function is used to create a tag name with required format
def create_tag_name(branch_name):
    tag_name = 'tag_' + current_date + '_' + branch_name
    return tag_name

# This function is used to create a tag
def create_tag(repo, tag_name, last_commit_id):
    try:
        tag_obj = repo.create_git_tag(tag=tag_name, message='New tag', type='commit', object=last_commit_id)
        repo.create_git_ref('refs/tags/{}'.format(tag_obj.tag), tag_obj.sha)
        return True
    except:
        return False

# This Function is used to delete a branch
def delete_branch(repo,branch_name):
    ref = repo.get_git_ref(f"heads/{branch_name}")
    ref.delete()

# This function will call create tag function and deleted branch function and
# Tag and delete the branches which are out of standards and
# Tag and delete Developer\ branch which doesn't have recent activity in last 90 days
def create_tag_and_delete_branch(repo_list):
    exception_file = open("exception.txt", encoding='utf-8-sig') 
    exception_list = exception_file.read().splitlines()
    for repo in repo_list:
        if repo.name.startswith('infra') == True:
            if repo.name in exception_list: #if repo is in exception list then print exception normalflow->els
                print(repo.name,":exception")
            else:
                branches = repo.get_branches()
                for branch in branches: 
                    if branch.name.lower().startswith('master') == False and branch.name.lower().startswith('release/') == False and\
                       branch.name.lower().startswith('developer/') == False:#all branches that doesnot start with master,main,release and developer
                        if branch.name.lower() != 'main':
                            print(repo.name)
                            repository_list.append(repo.full_name)
                            branch_list.append(branch.name)
                            # last_commit_id = get_last_commit_id(repo)
                            commit = branch.commit
                            last_commit_id = commit.sha
                            author_name = commit.commit.author.name
                            author_name_list.append(author_name)
                            tag_name = create_tag_name(branch.name)
                            tag_created = create_tag(repo, tag_name, last_commit_id)
                            try:
                                if tag_created == True:
                                    delete_branch(repo, branch.name)
                            except GithubException as e:
                                error = str(e)
                                print(error)
                                Failed_cases(repo.full_name,branch.name,author_name,error)
                    
                    if branch.name.lower().startswith('release/filmtrack') == False:
                        if branch.name.lower().startswith('developer/') == True or branch.name.lower().startswith('release/') == True:
                            last_modified = parse(branch.commit.author.last_modified)
                            now = datetime.now(timezone.utc)
                            last_activity = (now - last_modified)
                            if last_activity.days > 90:
                                repository_list.append(repo.full_name)
                                branch_list.append(branch.name)
                                commit = branch.commit
                                last_commit_id = commit.sha
                                author_name = commit.commit.author.name
                                author_name_list.append(author_name)
                                tag_name = create_tag_name(branch.name)
                                tag_created = create_tag(repo, tag_name, last_commit_id)
                                try:
                                    if tag_created == True:
                                        delete_branch(repo, branch.name)
                                except GithubException as e:
                                    error = str(e)
                                    print(error)
                                    Failed_cases(repo.full_name,branch.name,author_name,error)
                    #branch that would check the violation of naming standards
                    if branch.name.lower().startswith('release/filmtrack') == False and branch.name.lower().startswith('master') == False :
                        if branch.name.lower().startswith('developer/') == True or branch.name.lower().startswith('release/') == True:
                            nameList=['renjith','saravanan','vinoth','suresh','aamir','kiran','vinoth','bindu','rakesh','yash','sampath','bayaas','phani','rk','naganathan','ajeeth','harini','gokul','narendra','surya','sai',]
                            Transformed_newList=[]
                            for value in nameList:
                                 temp=value[0:3]
                                 Transformed_newList.append(temp)
                            flag=0
                            branchSplit=branch.name.lower().split('-')
                            lastelement=(branchSplit[-1])
                            #firstsplit=(branchSplit[0])
                            decider=branch.name.find('/') #to find the index of '/'
                            check = False
                            passed=0
                            #print(branch.name[decider+1])
                            if(len(branchSplit)<2): #if it doesnot contain"-" in repo
                                repository_list.append(repo.full_name)
                                branch_list.append(branch.name)
                                commit = branch.commit
                                last_commit_id = commit.sha
                                author_name = commit.commit.author.name
                                author_name_list.append(author_name)
                                tag_name = create_tag_name(branch.name)
                                tag_created = create_tag(repo, tag_name, last_commit_id)
                                try:
                                    if tag_created == True:
                                        delete_branch(repo, branch.name)
                                except GithubException as e:
                                    error = str(e)
                                    print(error)
                                    Failed_cases(repo.full_name,branch.name,author_name,error)
                                print("Doesnot follow standards No '-' \t"+branch.name +"\t",repo.full_name)
                            elif(branch.name[decider+1]!='-'):#imagine repo release/-renjith this has to be deleted as there is no feature name
                                for i in Transformed_newList:
                                    check=lastelement.find(i)#find function search if there is the same name is there if it is there it will return the index or it will return -1 if not present
                                    if(check!=-1):
                                        passed=1
                                        break
                                    continue
                                if (passed==0):
                                    repository_list.append(repo.full_name)
                                    branch_list.append(branch.name)
                                    # last_commit_id = get_last_commit_id(repo)
                                    commit = branch.commit
                                    last_commit_id = commit.sha
                                    author_name = commit.commit.author.name
                                    author_name_list.append(author_name)
                                    tag_name = create_tag_name(branch.name)
                                    tag_created = create_tag(repo, tag_name, last_commit_id)
                                    try:
                                        if tag_created == True:
                                            delete_branch(repo, branch.name)
                                    except GithubException as e:
                                        error = str(e)
                                        print(error)
                                        Failed_cases(repo.full_name,branch.name,author_name,error)
                                    print("Doesnot follow standards - no developer name \t"+branch.name+" "+repo.full_name)
                                else:
                                    print("The repo follows standards "+branch.name+" "+repo.full_name)
                            else:
                                repository_list.append(repo.full_name)
                                branch_list.append(branch.name)
                                # last_commit_id = get_last_commit_id(repo)
                                commit = branch.commit
                                last_commit_id = commit.sha
                                author_name = commit.commit.author.name
                                author_name_list.append(author_name)
                                tag_name = create_tag_name(branch.name)
                                tag_created = create_tag(repo, tag_name, last_commit_id)
                                try:
                                    if tag_created == True:
                                            delete_branch(repo, branch.name)
                                except GithubException as e:
                                    error = str(e)
                                    print(error)
                                    Failed_cases(repo.full_name,branch.name,author_name,error)
                                print("Doesnot follow standards - No feature name  \t "+branch.name+" "+repo.full_name)
    return repository_list, branch_list, author_name_list

# This function is used to create a csv report
def create_csv(repository_list, deleted_branch_or_tag_list, csv_name, **kwargs):
    dict = {
        'Repository': repository_list,
    }
    if kwargs.get('type') == 'branch':
        dict.update({'Branch': deleted_branch_or_tag_list,
                     'Author': kwargs.get('author')})
    elif kwargs.get('type') == 'tag':
        dict['tag_name'] = deleted_branch_or_tag_list
    elif kwargs.get('type') == 'Failure':
        dict.update({'Branch': deleted_branch_or_tag_list,
                     'Author': kwargs.get('author'),
                     'Error': kwargs.get('Error')})
    df = pd.DataFrame(dict)
    df.to_excel(csv_name, index=False)
    len_of_xl = len(df. index)
    return len_of_xl

# This function is used to the delete the Tags older then 100 days
def delete_old_tags(repo_list):
    repository_list = []
    for repo in repo_list:
        if repo.name.startswith('infra') == True:
            tags = list(repo.get_tags())
            for tag in tags:
                tag_created_date_str = tag.name.split('_')[1]
                tag_created_date = datetime.strptime(tag_created_date_str, DATE_FORMAT)
                date_to_delete = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=TAGS_CREATED_BEFORE_DAYS)
                if (tag_created_date <= date_to_delete):
                    repository_list.append(repo.full_name)
                    tag_list.append(tag.name)
                    ref = repo.get_git_ref(f"tags/{tag.name}")
                    ref.delete()
    return repository_list, tag_list

def Failed_cases(repo_name,branch_name,author_name,error):
    Failed_repos_list.append(repo_name)
    Failed_branch_list.append(branch_name)
    Failed_auth_name.append(author_name)
    Error.append(error)

# below lines will read mail.txt which contains the body of the mail
with open("mail.txt", encoding='utf-8-sig') as txt_file:
    output = txt_file.read() # might need .readlines() or .read().splitlines(). Whatever works for you
    Message = output

with open("error.txt", encoding='utf-8-sig') as txt_file:
    output = txt_file.read() # might need .readlines() or .read().splitlines(). Whatever works for you
    ERRMessage = output

with open("success.txt", encoding='utf-8-sig') as txt_file:
    output = txt_file.read() # might need .readlines() or .read().splitlines(). Whatever works for you
    EmptyMessage = output

# When ever we run the program it starts from here
if __name__ == "__main__":
    # Git authentication code to be given at runtime [Ex: python3 git_script.py guvcklwsfdjjwww]
    access_token = "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"
    git_login = Github(access_token)
    repo_list = [repo for repo in git_login.get_user().get_repos()]
    
    # below lines are used to call the function which will generate a report of all branches which all got tagged and deleted
    repository_list, deleted_branch_list, author_name_list = create_tag_and_delete_branch(repo_list)
    create_csv(repository_list, deleted_branch_list, 'repo_vs_deleted_branches_list_'+current_date+'.xlsx', type='branch', author=author_name_list)
    a = create_csv(repository_list, deleted_branch_list, 'repo_vs_deleted_branches_list_'+current_date+'.xlsx', type='branch', author=author_name_list)
    print('Tag creation and Branch deletion done!!')
    
    # below lines are used to call the function which will generate a report of all tags which all got deleted after 100 days of creation
    # repository_list, deleted_tags_list = delete_old_tags(repo_list)
    # create_csv(repository_list, deleted_tags_list, 'repo_vs_deleted_tags_list_'+current_date+'.xlsx', type='tag')
    # b = create_csv(repository_list, deleted_tags_list, 'repo_vs_deleted_tags_list_'+current_date+'.xlsx', type='tag')
    # print('Tag deletion done!!')
    
    # change below lines to "if a > 0 or b > 0:" if deleting tag is enabled
    # if a == 0:
    #     ses.ses(Message=EmptyMessage,type="Empty")
    # elif a > 0:
    #     ses.ses(Message=Message,branch_report='./repo_vs_deleted_branches_list_'+current_date+'.xlsx',tag_report='./repo_vs_deleted_tags_list_'+current_date+'.xlsx',type="Not Empty")
    
    # create_csv(Failed_repos_list, Failed_branch_list, 'failed_to_delete_'+current_date+'.xlsx', type='Failure', author=Failed_auth_name, Error=Error)
    # c = create_csv(Failed_repos_list, Failed_branch_list, 'failed_to_delete_'+current_date+'.xlsx', type='Failure', author=Failed_auth_name, Error=Error)
    # if c > 0:
    #     ses.ses(Message=ERRMessage,branch_report='./failed_to_delete_'+current_date+'.xlsx',type="Failure")
    # else:
    #     print('Standards Not voilated')
