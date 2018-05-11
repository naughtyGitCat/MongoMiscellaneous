replsetname ='sss'
TrueIP = '127.0.0.1'
port = '30000'
priority = '90'
# a = {"_id":replsetname,'members:[{host:'TrueIP:port',priority:{}}]}.format(replsetname,TrueIP,port,priority)
# print(a)
# a="{_id:'{}',members:[{host:'{}':'{}',priority:'{}'}]}".format(replsetname,TrueIP,port,priority)

a= {'_id':'{}'.format(replsetname),'members':[{'host':'{}:{}'.format(TrueIP,port),'priority':'{}'.format(priority)}]}
print(a)