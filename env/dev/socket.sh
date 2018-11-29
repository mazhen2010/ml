PROCESS=`ps -ef|grep socket_daemon|grep -v grep|grep -v PPID|awk '{ print $2}'`
for i in $PROCESS
do
  echo "Kill the socket_daemon process [ $i ]"
  kill -9 $i
done
basepath=$(cd `dirname $0`; pwd)
export zipline_conf=$basepath/sys_dev.conf
echo $zipline_conf
source ~/mazhen01/py_env/zipline/bin/activate
python ~/mazhen01/py_env/zipline/lib/python2.7/site-packages/zipline/socket_daemon.py
exit