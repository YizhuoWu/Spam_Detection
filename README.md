# Spam_Detection

In this project, we will Implement a machine learning model to predict whether a message is spam or not. Furthermore, we will create a system that upon receipt of an email message, it will automatically flag it as spam or not, based on the prediction obtained from the machine learning model.

DEVELOP MEMBER:
Jiashuo Liu - jl5922 (jl5922@columbia.edu)
Yizhuo Wu - yw3689 (yw3689@columbia.edu)

-------------------------------------------
Unique email address for testing:
test@columbiacoolkids.com

NOTE: You can change "test" as anything for testing, the Domain Identity is "columbiacoolkids.com".


-------------------------------------------
For cloudformation template:

1. When creating stack, there is one parameter for user to specify the Sagemaker Endpoint, the defalt value will be my own Sagemaker endpoint.

2. The cloudformation template created lambda functions, ses configurations, s3 bucket and all the corresponding IAM Roles/Policies.

![alt text](https://github.com/YizhuoWu/Spam_Detection/blob/main/diagram.png)
