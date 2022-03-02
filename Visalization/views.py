from django.shortcuts import render,redirect
import pandas as pd
from django.http import HttpResponse
import pandas as pd
import numpy as np
import re
from django.contrib.sites.shortcuts import get_current_site
import random
from django.contrib.auth.decorators import login_required
from  django.db.models import Q
from .forms import Registration_form,load_form,log_form
from .models import Registration,Uni_analysis
from django.contrib.auth import logout,login,authenticate
from  django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import  render_to_string
from django.core.mail import  send_mail
import hashlib
# Create your views here.
datasets_dict={}
user_file_names={}
def home(request):
    if request.method=="POST":
        filled_form=Registration_form(request.POST)
        if filled_form.is_valid():
            reg_username=filled_form.cleaned_data["username"]
            reg_password1=filled_form.cleaned_data["password1"]
            #reg_password2 = filled_form.cleaned_data["password2"]
            # print("username",username)
            # print("password",password)
            try:
                    User.objects.get(Q(username=reg_username))
                    status = "email id already existed"
                    form=Registration_form()
                    return render(request,"Visalization/home.html",{"reg_form":form,"status":status})

            except User.DoesNotExist:

                    reg_obj=User.objects.create_user(username=reg_username,password=reg_password1,email=reg_username)

                    # obj.save()
                    sender=settings.EMAIL_HOST_USER
                    rcv_name=re.findall('.+@',reg_username)[0]
                    reciever=reg_username
                    sub="Registration completed at Happy Analytics "

                    current_site = get_current_site(request)
                    name=rcv_name[:-1]
                    msg=render_to_string('Visalization/reg_success.html',
                                         {'user': name,
                                          'domain': current_site.domain
                                          }
                                         )
                    try:
                        send_mail(subject=sub,message=msg,from_email=sender,recipient_list=[reciever])
                        reg_obj.save()
                        return redirect("login_form")
                    except Exception as e:
                        print("This is exception while sending email",e)
                        form=Registration_form()
                        status="Please Turn on the internet"
                        return render(request, "Visalization/home.html", {"reg_form": form,"status":status})

            else:
                form=Registration_form()
                return render(request,"Visalization/home.html",{"reg_form":form})

        else:
            status="Registration failed"
            form=Registration_form()
            return render(request,"Visalization/home.html",{"reg_form":form,"status":status})

    form=Registration_form()
    return render(request,"Visalization/home.html",{"reg_form":form})



def login_form(request):

    if request.method=="POST":
        filled_form=log_form(request.POST)
        if filled_form.is_valid():
            logged_un=filled_form.cleaned_data["log_username"]
            logged_pwd=filled_form.cleaned_data["log_password"]
            try:
                user_data = User.objects.get(username=logged_un)

                user = authenticate(request, username=user_data.username, password=logged_pwd)
                if user != None:

                    login(request,user)
                    # print("This is the requested user",request.user)

                    return redirect('load')
                else:
                    status="Login Failed username or password mismatch"
                    form = log_form()
                    return render(request, 'Visalization/login.html', {"log_form": form,"status":status})
            except User.DoesNotExist:
                    #return HttpResponse({"user_id": "Invalid user ID."}, status=400)
                    status="User not registered"
                    form=log_form()
                    return render(request, 'Visalization/login.html', {"log_form": form,"status":status})

        else:
            form=log_form()
            return render(request,'Visalization/login.html',{"log_form":form})


    form=log_form()
    return render(request,'Visalization/login.html',{"log_form":form})

def logout_view(request):
    logout(request)
    return redirect('home')

# processed_dataset=""
# login_required(login_url='login/')
def load(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            filled_load_form=load_form(request.POST, request.FILES)
            print("filled dataset", filled_load_form)
            if filled_load_form.is_valid():

                #print(dir(request.FILES['file_upload']))
                #uploaded_dataframe=Extract_file_type(file_text=request.FILES['file_upload'].name,file_data=request.FILES['file_upload'])
                file_name=filled_load_form.cleaned_data["file_name"]
                user_file_names[request.user] = file_name
                uploaded_dataframe_exten = Extract_file_type(file_text=request.FILES['file_upload'].name)
                uploaded_dataframe= file_data=request.FILES['file_upload']

                #print("null data sum",dataframe.isnull().sum())
                #processed_dataset,mis_cells,mis_cells_per=Load(df=dataframe)

                processed_dataset,mis_count,mis_count_per,saved_dataset= Load(dataframe=uploaded_dataframe,file_type=uploaded_dataframe_exten,current_user=request.user)

                datasets_dict[request.user]=[processed_dataset,mis_count,mis_count_per,saved_dataset]




                return redirect("dashboard")
            else:
                print("form not valid")
        load_form_dataset=load_form()
        return render(request,'Visalization/load.html',{"load_dataset":load_form_dataset})
    else:
        return redirect("login_form")

def Extract_file_type(file_text):
    df_exten = re.findall('.xlsx$|.csv$|.txt$|.json$|.hdf$', file_text)

    return df_exten
def dataset_reading(file_data,df_exten,hdr):
    if ".xlsx" in df_exten[0]:
        df = pd.read_excel(file_data, header=hdr)

    elif ".csv" or ".txt" in df_exten[0]:
        df = pd.read_csv(file_data, header=hdr)

    elif ".json" in df_exten[0]:
        df = pd.read_json(file_data, header=hdr)

    elif ".hdf" in df_exten[0]:
        df = pd.read_hdf(file_data, header=hdr)

    else:
        df = pd.read_sql(file_data, header=hdr)
    return df

def Load(dataframe,header=0,file_type=None, missing_count=0, c=0, ca=0, dt=0, unsupport=0, *args, **kwargs):

        #Reading the Dataset
        df=dataset_reading(dataframe,file_type,header)
        print("*******************************This is printing top 10 records in dataset")
        print(df.head(10))

        # findout no of cols
        columns = df.shape[1]

        ## find out number of rows
        observations = df.shape[0]

        variables={}

        ## Find out number of missing cells in Dataset
        #list(df.isna().sum().values)
        for i in df.isna().sum():
            missing_count += i


        ## find out percentage of missing cells in Dataset

        missing_cells_per = "%.2f"%((missing_count/ (df.shape[1] * df.shape[0])) * 100)

        ### Detecting data type and Assign correct data type
        for i in df.columns:
            try:
                if re.findall("[a-zA-Z].*", str(df[i][0])):
                    df[i] = df[i].astype("object")
                elif "." in str(df[i][0]):
                    df[i] = df[i].astype("float64")
                elif str(df[i][0]).isnumeric():
                    df[i] = df[i].astype("int64")
                else:
                    pass
            except Exception as e:
                print(e)

        ### missing Data Handling
        res = df.apply(lambda x: "missing" if x.isnull().sum() > 0 else "no")
        for i in df.columns:
            if res[i] == "missing":

                missing_per_in_column = (df[i].isnull().sum() / df.shape[0]) * 100
                if missing_per_in_column > 35:
                    df.drop(i, axis=1, inplace=True)
                else:
                    if re.findall('int.+|float.+', str(df[i].dtype)):
                        mean_column = np.mean(df[i])
                        df[i] = df[i].replace(np.nan, mean_column)
                    else:

                        mode_data = df[i].mode()[0]
                        df[i] = df[i].replace(np.nan, mode_data)
        ## to save the file based on extensions they are uploaded
        key=list(kwargs.values())[0]
        try:
            if ".xlsx" in file_type[0]:
                saved_dataset = df.to_excel(user_file_names[key]+file_type[0])

            elif ".csv" or ".txt" in file_type[0]:
                saved_dataset = df.to_csv(user_file_names[key]+file_type[0])

            elif ".json" in file_type[0]:
                saved_dataset = df.to_json(user_file_names[key]+file_type[0])

            elif ".hdf" in file_type[0]:
                saved_dataset = df.to_hdf(user_file_names[key]+file_type[0])

            else:
                saved_dataset = df.to_sql(user_file_names[key]+file_type[0])
        except:
            return redirect('load')

        return df,missing_count,missing_cells_per,saved_dataset

def dashboard(request):
    if request.user.is_authenticated:
        try:
            dict_data=datasets_dict[request.user]
            processed_dataset=dict_data[0]
            missing_cells=dict_data[1]
            missing_cells_per=dict_data[2]
            saved_dataset=dict_data[-1]
            # print(processed_dataset.columns)
            # print("missing cells",missing_cells)
            # print("missing cells per",missing_cells_per)
            # print(processed_dataset.info())
            if len(processed_dataset) !=0:
                # print("This is dataset appear in dashboard",processed_dataset.shape)
                # findout no of cols

                columns = processed_dataset.shape[1]

                ## find out number of rows
                observations = processed_dataset.shape[0]

                variables = {}
                c=0
                ca=0
                dt=0
                unsupport=0
                # days=pd.DatetimeIndex(processed_dataset["Date"]).day
                # print("days are",days)
                ## detect dtype and assign correct data type into columns in Dataset
                num_columns=[]
                cat_columns=[]
                date_columns=[]
                for i in zip(processed_dataset.columns, processed_dataset.dtypes):
                    if len(re.findall("int.+|float.+", str(i[1]))):
                        c += 1

                        if str(i[0])=='Latitude' or str(i[0])=='Lattitude'  or str(i[0])=='Longtitude' or str(i[0])=='Longitude' or re.findall('^Lat.+de$',str(i[0])) or re.findall('^Lon.+de$',str(i[0])) or str(i[0])=='id':
                            continue
                        else:
                            num_columns.append(str(i[0]))
                    elif len(re.findall("object|Object", str(i[1]))):
                        ca += 1
                        cat_columns.append(str(i[0]))
                    elif len(re.findall("datetime.+", str(i[1]))):
                        dt += 1
                        date_columns.append(str(i[0]))
                    else:
                        unsupport += 1


                variables["number_of_numerical_variables"] = c
                variables["number_of_categorical_variables"] = ca
                variables["number_of_datetime_variables"] = dt
                variables["number_of_unsupported_variables"] = unsupport

                l=[]

                for k,v in variables.items():
                    l.append(k+":"+str(v))

                ## data for charts
                ## handling date time columns
                if len(date_columns)>=1:
                    processed_dataset["months"]=pd.DatetimeIndex(processed_dataset[date_columns[0]]).month
                    processed_dataset["year"]=pd.DatetimeIndex(processed_dataset[date_columns[0]]).year
                    # for i in num_columns:
                    #     cal_distinct_val=list(np.unique(processed_dataset[i]))

                    from collections import defaultdict
                    rgb=[]
                    months_data={}
                    years_data={}
                    months_dataset = []
                    years_dataset=[]

                # dataset = defaultdict(list)

                #'rgb(234, 192, 192)'
                    for i in num_columns:
                            ##assumptions unique counts are >50
                            uni_values=len(np.unique(processed_dataset[i]))


                            if i=="Longtitude" or i== "Lattitude":
                                continue
                            elif uni_values<=50:
                                a= random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                                rgb.append('rgb'+str(a))
                                months_dataset.append({"data":[ "%.2f"%dt for dt in  processed_dataset.groupby(by="months").mean()[i].values] ,"label":i,"borderColor":rgb[-1],"tension": 0.1})
                                years_dataset.append({"data":[ "%.2f"%dt for dt in  processed_dataset.groupby(by="year").mean()[i].values],"label":i,"borderColor":rgb[-1],"tension": 0.1,"pointStyle": 'circle',
                  "pointRadius": 7,
                  "pointHoverRadius": 15})

                    months_data["labels"]=list(np.unique(processed_dataset["months"]))
                    months_data["datasets"] = months_dataset
                    years_data["labels"]=list(np.unique(processed_dataset["year"]))
                    years_data["datasets"]=years_dataset
                else:
                    pass



    #### This logic for the line charts  (working on numerical columns)  Univariavte Analysis
                num_dataset={}
                uni_dataset=[]
                render_list=[]
                graph=[]
                rgb=[]
                can_ids=[]
                x_axis=[]
                y_axis=[]
                title=[]
                for i in processed_dataset[num_columns]:
                    ## this is assumptions for creating univariate charts
                    if len(np.unique(processed_dataset[i])) <=20:

                        b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                        rgb.append('rgb' + str(b))
                        uni_dataset.append(
                            {"data": list(processed_dataset[i].value_counts().values),
                             "label": i, "borderColor": rgb[-1], "tension": 0.1})
                        num_dataset["labels"] = list(np.unique(processed_dataset[i]))
                        num_dataset["datasets"]=uni_dataset
                        render_list.append(num_dataset)
                        can_ids.append(i)
                        x_axis.append(i)
                        y_axis.append("Column unique values count")
                        title.append("X-axis"+"("+str(i)+")"+" "+"vs"+" "+"Y-axis"+"("+y_axis[0]+")")
                        num_dataset={}
                        uni_dataset=[]
                uni_data=zip(render_list,can_ids,x_axis,y_axis,title)
                # print("This is the chart data (labels and dataset)",render_list)
                # print("This is the canvas is's for chart rendering")



    #### Multivariate analysis on umerical data
                scatter_list=[]
                colors=[]
                scatter_can_id=[]
                x_axis=[]
                y_axis=[]


                for i in range(len(num_columns)-1):

                    current=num_columns[i]  ## col1
                    next_data=num_columns[i+1]   ## col2
                    b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                    colors.append('rgb' + str(b))
                    scatter_list.append(
                                            {"datasets":
                                                    [{   "label": str(current) + " " + "vs" + " " + str(next_data),
                                                        "data":[{'x': i,'y':j} for i,j in zip(list(processed_dataset[current].values),list(processed_dataset[next_data].values))],
                                                        "backgroundColor": colors[-1]
                                                    }]
                                             }
                                            )
                    scatter_can_id.append(str(current+"_"+next_data))
                    x_axis.append(current)
                    y_axis.append(next_data)
                scatter_zipped=zip(scatter_list,scatter_can_id,x_axis,y_axis)

    ## Categorical Analysis -- Univariate Analysis
                can_ids_for_catvar=[]
                cat_render_list=[]
                cat_list=[]
                for i in cat_columns:
                    if len(processed_dataset[i].value_counts().keys()) <= 50:
                        can_ids_for_catvar.append(i)
                        cat_list.append(
                                    {
                                        "labels": [label for label in processed_dataset[i].value_counts().keys()],
                                        "datasets": [{
                                                            "axis": 'y',
                                                            "label": i,
                                                            "data": list(processed_dataset[i].value_counts().values),
                                                            "backgroundColor": [
                                                                                'rgba(255, 99, 132, 0.9)',
                                                                                'rgba(255, 159, 64, 0.2)',
                                                                                'rgba(255, 205, 86, 0.2)',
                                                                                'rgba(75, 192, 192, 0.2)',
                                                                                'rgba(54, 162, 235, 0.2)',
                                                                                'rgba(153, 102, 255, 0.2)',
                                                                                'rgba(201, 203, 207, 0.2)'
                                                                                ],
                                                            "borderColor": [
                                                                                'rgb(255, 99, 132)',
                                                                                'rgb(255, 159, 64)',
                                                                                'rgb(255, 205, 86)',
                                                                                'rgb(75, 192, 192)',
                                                                                'rgb(54, 162, 235)',
                                                                                'rgb(153, 102, 255)',
                                                                                'rgb(201, 203, 207)'
                                                                            ],
                                                            "borderWidth": 1
                                                        }]
                                    }

                                               )

                cat_render_list=zip(cat_list,can_ids_for_catvar)
                if len(date_columns)>=1:
                    return render(request,'Visalization/demo.html',
                        {"variables_data":l,"miss_cells":missing_cells,"miss_cells_percent":missing_cells_per,"cols":columns,"obser":observations,
                          "date_chart_month":months_data,"date_chart_year":years_data,"uni_data":uni_data,"scatter_data":scatter_zipped,
                         "cat_uni_data":cat_render_list,"saved_dataset_status":saved_dataset
                         })
                else:
                    return render(request, 'Visalization/demo.html',
                                  {"variables_data": l, "miss_cells": missing_cells,
                                   "miss_cells_percent": missing_cells_per, "cols": columns, "obser": observations,"uni_data": uni_data,
                                   "scatter_data": scatter_zipped,
                                   "cat_uni_data": cat_render_list, "saved_dataset_status": saved_dataset
                                   })

            else:
                return HttpResponse("Please upload dataset")
        except KeyError:
            # form=load_form()
            status="Please upload dataset"
            return render(request,'Visalization/load.html',{"status":status})
    else:
        return redirect('login_form')


