from django.shortcuts import HttpResponse
import json
from myAdmin.models import *
from django.db import transaction
import datetime
from django.db.models import Sum


############################################################
#功能：问卷设计者操作主入口
#最后更新：2019-05-23
############################################################
def opera(request):
    response={'code':0,'msg':'success'}
    if request.method=='POST':
        body=str(request.body,encoding='utf-8')
        print(body)
        try:
            info = json.loads(body)#解析json报文
        except:
            response['code'] = '-2'
            response['msg'] = '请求格式有误'
        else:
            opera_type = info.get('opera_type')  # 获取操作类型
            username = request.session.get('username')
            if opera_type:#如果操作类型不为空
                if opera_type == 'login':
                    response = login(info, request)
                elif opera_type == 'logincheck':
                    response = loginCheck(request)
                elif opera_type == 'register':
                    response = register(info)
                elif opera_type == 'resetpass':
                    response = resetpass(info)
                elif username:#需要验证username的方法
                    if opera_type == 'add_wj':  # 添加问卷
                        response = addWj(info,username)
                    elif opera_type == 'get_wj_list':  # 获取问卷列表
                        response = getWjList(info,username)
                    elif opera_type == 'delete_wj':  # 删除问卷
                        response = deleteWj(info,username)
                    elif opera_type == 'get_question_list':  # 获取问题列表
                        response = getQuestionList(info,username)
                    elif opera_type == 'add_question':  # 添加问题
                        response = addQuestion(info,username)
                    elif opera_type == 'delete_question':  # 删除问题
                        response = deleteQuestion(info,username)
                    elif opera_type == 'push_wj':  # 发布问卷（更改问卷状态）
                        response = pushWj(info,username)
                    elif opera_type == 'dataAnalysis':#获取统计数据
                        response = dataAnalysis(info)
                    elif opera_type == 'add_temp':#添加模板
                        response = addTemp(info,username)
                    elif opera_type == 'use_temp':#添加模板
                        response = useTemp(info,username)
                    elif opera_type == 'exit':
                        response = exit(request)
                    else:
                        response['code'] = '-7'
                        response['msg'] = '请求类型有误'
            else:
                response['code'] = '-3'
                response['msg'] = '确少必要参数'
    else:
        response['code']='-1'
        response['msg']='请求方式有误'
    return HttpResponse(json.dumps(response))


def loginCheck(request):
    response = {'code': 0, 'msg': 'success'}
    # 查询django_session中是否有username，查询失败抛出异常
    # 查询成功判断username是否为空，若为空，返回404错误，不为空，返回成功信息
    try:
        username = request.session.get('username')
    except:
        response['code']='-4'
        response['msg']='操作失败'
    else:
        print(username)
        if username:
            response['data']={'user':username}
        else:
            response['code'] = '404'
            response['msg'] = '未登录'
    return response



############################################################
#功能：添加问卷/更新问卷
#最后更新：2020-06-19
#备注：当传入id(问卷id)为空时：添加问卷  不为空时：更新问卷
############################################################
def addWj(info,username):
    response = {'code': 0, 'msg': 'success'}
    title = info.get('title')#问卷标题
    desc=info.get('desc')#问卷描述
    register=info.get('register')#是否必须注册
    totalnumber=info.get('totalnumber')
    daynumber=info.get('daynumber')
    days=info.get('days')
    id=info.get('id')#问卷id 可为空
    if username and title:
        try:
            if id:#id不为空 更新问卷
                res=Wj.objects.get(username=username,id=id)
                res.title=title
                res.desc=desc
                if(register):
                    res.register=register
                else:
                    res.register=0
                print("1")
                if(totalnumber):
                    res.totalnumber=totalnumber
                else:
                    res.totalnumber=0
                print("2")          
                if(daynumber):
                    res.daynumber=daynumber #如果缺省 即没有传入参数 0默认为不限制
                else:
                    res.daynumber=0
                print("The totalnumber is")
                print(res.totalnumber)
                print(res.daynumber)
                if(res.totalnumber<res.daynumber):
                    print("填写数量不合理")
                    response['code'] = '-4'
                    response['msg'] = '填写数量不合理'
                    return response
                if(days):
                    res.days=days
                else:
                    res.days=-1
                res.save()
            else:#否则 添加问卷  
                if(register):
                    print("If has,the register is")
                    print(register)
                else:
                    register=0
                print(register)
                if(totalnumber):
                    print("If has,the totalnumber is")
                    print(totalnumber)
                else:
                    totalnumber=0
                print("So the totalnumber is")
                print(totalnumber)
                if(daynumber):
                    print("If has,the daynumber is")
                    print(daynumber)#如果缺省 即没有传入参数 0默认为不限制
                else:
                    daynumber=0
                print("So the daynumber is")
                print(daynumber)
                if(daynumber > totalnumber):
                    print("填写数量不合理")
                    print(daynumber)
                    print(">")
                    print(totalnumber)
                    print("?")
                    response['code'] = '-4'
                    response['msg'] = '填写数量不合理'
                    return response
                if(days==''):
                    days=-1
                res = Wj.objects.create(username=username, title=title,desc=desc, status=0,register=register,totalnumber=totalnumber,daynumber=daynumber,totalrecord=0,dayrecord=0,days=days)
        except:
            response['code'] = '-4'
            response['msg'] = '操作失败'
        else:
            if res.id > 0:
                response['id'] = res.id
            else:
                response['code'] = '-4'
                response['msg'] = '操作失败'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response



############################################################
#功能：获取问卷列表
#最后更新：2019-05-27
############################################################
def getWjList(info,username):
    response = {'code': 0, 'msg': 'success'}
    if username:
        obj = Wj.objects.filter(username=username).order_by('-id')
        detail=[]
        for item in obj:
            temp={}
            temp['id']=item.id
            temp['title']=item.title
            temp['desc']=item.desc
            temp['status']=item.status
            temp['register']=item.register
            if(item.totalnumber==0):
                temp['totalnumber']=''
            if(item.daynumber==0):
                temp['daynumber']=''
            if(item.days==-1):
                temp['days']=''
            detail.append(temp)
        response['data']={'detail':detail}

    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response



############################################################
#功能：删除问卷
#最后更新：2019-05-23
############################################################
def deleteWj(info,username):
    response = {'code': 0, 'msg': 'success'}
    id = info.get('id')#问卷id
    if username and id:
        try:
            Wj.objects.filter(username=username, id=id).delete()#删除问卷
            obj=Question.objects.filter(wjId=id)#查询所有关联问题
            for item in obj:
                Options.objects.filter(questionId=item.id).delete()#删除问题关联的选项
            obj.delete()#删除问卷所有关联问题

            Submit.objects.filter(wjId=id).delete()#删除该问卷的提交信息
            Answer.objects.filter(wjId=id).delete()#删除该问题的所有回答
        except:
            response['code'] = '-4'
            response['msg'] = '操作失败'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response




############################################################
#功能：获取问题列表
#最后更新：2019-05-27
############################################################
def getQuestionList(info,username):
    response = {'code': 0, 'msg': 'success'}
    wjId=info.get('wjId')#wjid
    index=1
    if username:
        res=Wj.objects.filter(id=wjId,username=username)
        if res.exists():#判断该问卷id是否为本人创建
            obj=Question.objects.filter(wjId=wjId)
            detail=[]
            Theoptions={}
            TheQuestion={}
            RelatedOption={}
            for item in obj:
                temp={}
                temp['title']=item.title
                temp['type']=item.type
                temp['id']=item.id#问题id
                TheQuestion[item.id]=index
                index=index+1
                temp['row']=item.row
                temp['must']=item.must
                temp['numbertype']=item.numbertype
                temp['lowdesc']=item.lowdesc
                temp['highdesc']=item.highdesc
                temp['relatedId']=item.relatedId
                temp['relatedOp']=item.relatedOp
                temp['selftype']=item.selftype
                #获取选项
                temp['options']=[]
                if temp['type'] in ['radio', 'checkbox'] or temp['selftype'] in ['radio', 'checkbox']:  # 如果是单选或者多选
                    optionItems = Options.objects.filter(questionId=item.id)
                    for optionItem in optionItems:
                        temp['options'].append({'title': optionItem.title, 'id': optionItem.id})
                        RelatedOption[optionItem.id]=optionItem.title
                temp['radioValue']=-1#接收单选框的值
                temp['checkboxValue'] =[]#接收多选框的值
                temp['textValue']=''#接收输入框的值
                detail.append(temp)  #将该问题加入问题列表！！！！！！！！！！！！
                Theoptions[item.id]=temp['options']
            response['detail']=detail
            response['options']=Theoptions
            response['TheQuestion']=TheQuestion# id -> index
            response['RelatedOption']=RelatedOption
        else:
            response['code'] = '-6'
            response['msg'] = '权限不足'

    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    #print("RelatedOption!!!!!!!!!!!!!!!")
    #print(RelatedOption)
    return response





############################################################
#功能：添加问题/更新问题
#最后更新：2019-05-23
#备注：当传入questionId(问题id)为空时：添加问题  不为空时：更新问题
############################################################
#事务处理  当一次插入选项过多时（测试10个选项要5秒以上）很费时间 增加事务处理可大大加快速度（改进后20个选项3秒插入完成）
@transaction.atomic
def addQuestion(info,username):  # info中的numbertype
    response = {'code': 0, 'msg': 'success'}
    wjId=info.get('wjId')#wjid
    q_title=info.get('title')#题目标题
    q_type=info.get('type')#题目类型
    q_numbertype = info.get('numbertype')
    options=info.get('options')#选项
    row=info.get('row')
    must=info.get('must')
    questionId=info.get('questionId')#问题id 可为空
    lowdesc=info.get('lowdesc')
    highdesc=info.get('highdesc')
    relatedId=info.get('relatedId')
    relatedOp=info.get('relatedOp')
    selftype=info.get('selftype')
    if wjId and q_title and q_type and must!=None:
        if q_type in ['radio','checkbox','text','number','score','cascade','location']:
            if questionId:#问题id存在 更新问题
                newIds=[]
                for temp in options:
                    newIds.append(temp['id'])#将更新后的选项id记录
                allOptions=Options.objects.filter(questionId=questionId)
                #遍历选项 把不在更新后的选项id中的选项删除
                for option in allOptions:
                    if option.id not in newIds:
                        option.delete()
                #更新问题
                Question.objects.filter(wjId=wjId,id=questionId).update(title=q_title,type=q_type,must=must,row=row,numbertype=q_numbertype,lowdesc=lowdesc,highdesc=highdesc,relatedId=relatedId,relatedOp=relatedOp,selftype=selftype)
                #更新选项
                for option in options:
                    if option['id']!=0:#选项为已有的 更新
                        Options.objects.filter(questionId=questionId, id=option['id']).update(title=option['title'])
                    else:#选项为新增的 添加
                        Options.objects.create(questionId=questionId,title=option['title'])
            else:#问题id不存在 添加问题
                # 添加问题
                print("1")
                resObj = Question.objects.create(wjId=wjId, title=q_title, type=q_type, row=row,must=must,numbertype=q_numbertype,lowdesc=lowdesc,highdesc=highdesc,relatedId=relatedId,relatedOp=relatedOp,selftype=selftype)
                print(relatedId)
                questionId = resObj.id
                response['id'] = questionId
                # 添加选项
                if q_type == 'radio' or q_type == 'checkbox' or selftype == 'radio' or selftype == 'checkbox':  # 单选或者多选
                    print(type(options))
                    if options and type(options) == type([]):
                        for item in options:
                            Options.objects.create(questionId=questionId, title=item['title'])
                            # Options(questionId=questionId,title=item)
                    else:  # 传入选项不能为空
                        response['code'] = '-4'
                        response['msg'] = '操作失败'
        else:
            response['code'] = '-5'
            response['msg'] = '传入参数值有误'
            return response
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response


############################################################
#功能：删除问题
#最后更新：2019-05-23
############################################################
@transaction.atomic
def deleteQuestion(info,username):
    response = {'code': 0, 'msg': 'success'}
    questionId=info.get('questionId')
    if questionId and username:
        try:
            s_wjId=Question.objects.get(id=questionId).wjId#该题目所属的问卷id
            s_username=Wj.objects.get(id=s_wjId).username#该题目所属的用户名
            if username==s_username:#该题目是此用户创建的 有权限删除
                Question.objects.filter(id=questionId).delete()#删除问题
                Options.objects.filter(questionId=questionId).delete()#删除关联选项
            else:#该题目不是此用户创建的 无权限删除
                response['code'] = '-6'
                response['msg'] = '权限不足'
        except:
            response['code'] = '-4'
            response['msg'] = '操作失败'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response



############################################################
#功能：发布问卷
#最后更新：2019-05-24
############################################################
def pushWj(info,username):
    response = {'code': 0, 'msg': 'success'}
    wjId=info.get('wjId')
    status=info.get('status')#0暂停问卷 1发布问卷
    OpenTime=datetime.datetime.now()
    print("发布问卷！")
    print(OpenTime)
    print('%s,%s,%s'%(wjId,username,status))
    if wjId and username and (status==0 or status==1):
        res=Wj.objects.filter(id=wjId,username=username)
        if res.exists():  # 该题目是此用户创建的 有权限
            res.update(status=status)
            res.Opentime=OpenTime
            res.update(OpenTime=OpenTime)
        else:  # 该题目不是此用户创建的 无权限
            response['code'] = '-6'
            response['msg'] = '权限不足'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'

    return response




############################################################
#功能：登录
#最后更新：2019-05-28
############################################################
def login(info,request):
    response = {'code': 0, 'msg': 'success'}
    username = info.get('username')  #用户名
    password = info.get('password')  #密码
    if username and password:
        try:
            # 根据前台传回的用户名查找密码和用户状态
            # 若查询失败，抛出异常错误
            # 若查询成功，判断密码是否正确和用户状态是否正常
            t_password = User.objects.get(username=username).password
            t_status = User.objects.get(username=username).status
        except:
            response['code'] = '-5'
            response['msg'] = '不存在该用户'
        else:
            if password==t_password and 0==t_status:
                request.session["username"]= username
                return response
            else:
                response['code'] = '-4'
                response['msg'] = '操作失败'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response

############################################################
#功能：退出登录
#最后更新：2019-05-28
############################################################
def exit(request):
    response = {'code': 0, 'msg': 'success'}
    # 对django_session中的用户名执行删除操作
    # 若删除成功，返回成功信息
    # 若删除失败，抛出异常操作失败
    try:
        del request.session['username']
    except:
        response['code'] = '-4'
        response['msg'] = '操作失败'
    else:
        return response
    return response



############################################################
#功能：注册
#最后更新：2019-05-29
############################################################
def register(info):
    response = {'code': 0, 'msg': 'success'}
    t_username = info.get('username') #用户名
    t_password = info.get('password') #密码
    t_email = info.get('email') #邮箱
    if t_username and t_password and t_email:  #用户名和密码和邮箱不为空时，执行操作
        #先判断email是否唯一
        emailItems = User.objects.filter(email=t_email)
        print("the email are:")
        print(emailItems)
        if(emailItems):
            print("already!")
            response['code'] = '-5'
            response['msg'] = '操作失败'
            return response
        #将用户名和密码，以及初始状态status=0插入数据库中
        #若插入失败，抛出异常操作失败
        #若插入成功，返回成功信息
        try:
            User.objects.create(username=t_username,password=t_password,email=t_email)
        except:
            response['code'] = '-4'
            response['msg'] = '操作失败'
        else:
            return response
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response

############################################################
#功能：重置密码
#最后更新：2019-05-28
############################################################
def resetpass(info):
    response = {'code': 0, 'msg': 'success'}
    username = info.get('username') #用户名
    email = info.get('email') #邮箱
    if username and email:#用户名和邮箱不为空，执行操作
        #根据用户名查询对应邮箱是否正确
        #若正确，返回成功信息，若不正确，抛出异常
        try:
            t_email = User.objects.get(username=username).email
        except:
            response['code'] = '-5'
            response['msg'] = '不存在该用户'
        else:
            if email==t_email:
                return response
            else:
                response['code'] = '-10'
                response['msg'] = '未绑定邮箱'
    else:
        response['code'] = '-3'
        response['msg'] = '确少必要参数'
    return response


############################################################
#功能：数据分析
#最后更新：2019-05-28
############################################################
def dataAnalysis(info):
    response = {'code': 0, 'msg': 'success'}
    total=[]
    try:
        wjId=info.get('wjId')#获取问卷id
    except:
        response['code'] = '-4'
        response['msg'] = '操作失败'
    else:
        if wjId:  # 如果问卷id 存在
            detail = []
            print(wjId)
            res=Wj.objects.get(id=wjId)
            response['Opentime']=res.OpenTime.strftime("%Y-%m-%d %H:%M:%S")
            if(res.days!=-1):#如果有填写周期限制的话   
                closetime=(res.OpenTime+datetime.timedelta(days=res.days)).strftime("%Y-%m-%d %H:%M:%S")
                response['Closetime']=closetime
            else:
                response['Closetime']=''
            submit = Submit.objects.filter(wjId=wjId)
            response['Submit']=submit.count()
            questions = Question.objects.filter(wjId=wjId)
            for question in questions:
                questionTitle = question.title
                questionType = question.type
                selftype = question.selftype
                if questionType == "radio" or questionType == "checkbox" or questionType == "score" or selftype == "radio" or selftype == "checkbox" or selftype == "score":
                    result = getQuestionAnalysis(question.id)
                    print(result)
                elif questionType == "text" or selftype == "text":
                    result = getQuestionText(question.id)
                elif questionType == "number" or selftype == "number":
                    result = getQuestionText(question.id)
                    total=getsum(question.id)
                    #Totalnumber = getTotal(question.id)#获得总数
                detail.append({
                    "title": questionTitle,
                    "type": questionType,
                    "result": result,
                    "selftype":selftype,
                    "total":total
                })
            response['detail'] = detail
        else:
            response['code'] = '-3'
            response['msg'] = '确少必要参数'
    return response


#根据问题id获取统计情况
def getQuestionAnalysis(questionId):
    options=Options.objects.filter(questionId=questionId)   #获取问题的选项
    print("Options")
    print(options)
    answer = Answer.objects.filter(questionId=questionId)  # 获取问题id的答案
    print("Answers")
    print(answer)
    total = answer.count()  # 获取答案的总数
    result=[]
    index=0
    for option in options:
        optionTitle=option.title#获取问题选项
        optionCount=Answer.objects.filter(questionId=questionId,answer=index).count()#获取每个选项数量
        if total==0:
            percent=0
        else:
            percent=int((optionCount/total)*10000)/100#获取每个选项的占比
        result.append({
            "option":optionTitle,
            "count":optionCount,
            "percent":str(percent)+'%'
        })
        index=index+1
    return result
#获取文本内容
def getQuestionText(questionId):
    answer = Answer.objects.filter(questionId=questionId)# 获取问题id的答案
    result=[]
    for item in answer:
        if(item.answer):
            result.append({'context': item.answer})
    return result

#获取数字题相加  直接添加那个相加的总和即可 
def getsum(questionId):
    answer = Answer.objects.filter(questionId=questionId)# 获取问题id的答案
    result=[]
    total=0
    for item in answer:
        if(item.answer):
            total+=float(item.answer)
    print("The total number is ")
    print(total)
    result.append({'context': total})
    return result


