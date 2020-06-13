function queryGateways() {
    let gateways =
        [{x:22, y:6.41}, {x:22.62, y:22.59}, {x:41, y:17.4},
        {x:31.875, y:2.29}, {x:8.35, y:22.59}, {x:8.15, y:3.31}];

    let width=637.5
    let height=435
    d3.select("svg").remove()
    let svg = d3.select("#map")
                .append("svg")
                .attr("width", width)
                .attr("height", height)

    const colorMap = d3.interpolateRgb(
                      d3.rgb('#7CFC00'),
                      d3.rgb('#800000')
                    )

    var request = new Request('http://localhost:8010/proxy/api/gateways');
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                for (let i = 0; i < data.length; i++) {
                    gateways[i].number=data[i].connections;
                 }
                 let circles = svg.selectAll(".MyCircle")
                        .data(gateways)
                        .enter()
                        .append("circle")
                        .attr("class","MyCircle")
                        .attr("cx", function(d){
                            return d.x*15;
                        } )
                        .attr("cy",function(d){
                            return height-d.y*15;
                        })
                        .attr("fill", (d)=> {
                            return colorMap(d.number)
                        })
                        .attr("r","8");
            });
        }).catch(function(error) {
          alert("Can't connected to server!", error)
        });
}

function drawPoint (point){
    let width=637.5
    let height=435
    let svg = d3.select("svg")
    let circles = svg.append("circle")
            .attr("class","MyCircle")
            .attr("cx", point[0].x*15)
            .attr("cy",height-point[0].y*15)
            .attr("fill", point[0].color)
            .attr("r","3");
}

function drawTrace (mac,startTime,endTime,color='#8B0000') {
    let url="http://localhost:8010/proxy/device/trace?start="+
    startTime+"&end="+endTime+"&mac="+mac;
    var request = new Request(url);
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                let trace=data.data[0].trace;
                //console.log(trace)
                if(trace.length==1){
                    drawPoint([{x:trace[0].x,y:trace[0].y,color:color}])
                }
                let points=[]
                let len=trace.length
                for (let i = 0; i < len; i++) {
                    points.push({x:trace[i].x*15,y:trace[i].y*15});
                }
                for (let i = 0; i <len; i++) {
                    let sumX=points[i].x
                    let sumY=points[i].y
                    let count=1
                    if(i-2>=0){
                        sumX+=points[i-2].x
                        sumY+=points[i-2].y
                        count+=1
                    }
                    if(i-1>=0){
                        sumX+=points[i-1].x
                        sumY+=points[i-1].y
                        count+=1
                    }
                    if(i+1<len){
                        sumX+=points[i+1].x
                        sumY+=points[i+1].y
                        count+=1
                    }
                    if(i+2<len){
                        sumX+=points[i+2].x
                        sumY+=points[i+2].y
                        count+=1
                    }
                    points[i].x=sumX/count
                    points[i].y=sumY/count
                }

                let width=637.5
                let height=435
                const line = d3.line()
                      .x((d)=> d.x)
                      .y((d)=> height - d.y)
                      //.curve(d3.curveLinear)
                      .curve(d3.curveNatural)
                      //.curve(d3.curveMonotoneX)
                      //.curve(d3.curveCatmullRom)
                //console.log(points)
                d3.select('svg')
                  .append("path")
                  .attr('d', line(points))
                  .attr('fill', 'none')
                  .attr('stroke-width',2)
                  .attr('stroke', color);
            })
        })
}

function queryDevices(){
    //let url="http://localhost:8010/proxy/api/devices/"+document.getElementById("macAddr").value+"/traces?start_time=2020-04-07%2012:25:00&end_time=2020-04-07%2013:45:00";
    let url="http://localhost:8010/proxy/device/trace?mac=74:f6:1c:03:c3:a9&start=2020-04-15-16-00-00&end=2020-04-15-16-32-00";
    var request = new Request(url);
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                data=data.data[0].trace;
                //console.log(data)
                let points=[]
                for (let i = 0; i < data.length; i++) {
                    if(data[i].x>0.1&&data[i].y>0.1)
                        points.push({x:data[i].x*15,y:data[i].y*15});
                }

                //points=[{x:22*15, y:6.41*15}, {x:22.62*15, y:22.59*15}, {x:41*15, y:17.4*15}];

                let width=637.5
                let height=435
                d3.select("svg").remove()
                let svg = d3.select("#map")
                            .append("svg")
                            .attr("width", width)
                            .attr("height", height)
                const line = d3.line()
                      .x((d)=> d.x)
                      .y((d)=> height - d.y)
                      //.curve(d3.curveLinear)
                      //.curve(d3.curveNatural)
                      //.curve(d3.curveMonotoneX)
                      .curve(d3.curveCatmullRom)
                //console.log(points)
                d3.select('svg')
                  .append("path")
                  .attr('d', line(points))
                  .attr('fill', 'none')
                  .attr('stroke-width',2)
                  .attr('stroke', 'green');
        }).catch(function(error) {
          alert("Can't connect to server!", error)
        });
})
        .catch(function(error) {
          alert("Can't connected to server!", error)
        });;
}

/*trace:[{
      "x": 7.8977438856596995,
      "y": 3.09109512272798,
      "location": "7",
      "step": 0
    }]*/
function queryTraceFromMac(macAddress1,macAddress2){
    var date = new Date();
    startTime=getTimeFromCurrent(10)
    endTime=getTimeFromCurrent(0)
    let url1="http://localhost:8010/proxy/device/trace?mac="+macAddress1+"&start="+startTime+"&end="+endTime;
    let url2="http://localhost:8010/proxy/device/trace?mac="+macAddress2+"&start="+startTime+"&end="+endTime;
    //url1="http://localhost:8010/proxy/device/trace?mac=c5:e1:3b:6b:0c:8f&start=2020-04-15-02-11-00&end=2020-04-15-02-12-00"
    //url2="http://localhost:8010/proxy/device/trace?mac=c5:e1:3b:6b:0c:8f&start=2020-04-15-02-11-00&end=2020-04-15-02-12-00"
    //url2="http://localhost:8010/proxy/device/trace?mac=74:f6:1c:03:c3:a9&start=2020-04-15-16-00-00&end=2020-04-15-16-32-00";
    var request1 = new Request(url1);
    var request2 = new Request(url2);
    fetch(request1,{mode: 'cors'})
        .then(function(response1) {
          res1=response1.json();
          res1.then(
            data1=>{
                let traceX=data1.data[0].trace;
                fetch(request2,{mode: 'cors'})
                    .then(function(response2) {
                      res2=response2.json();
                      res2.then(
                        data2=>{
                            drawTrace(traceX)
                            let traceY=data2.data[0].trace;
                            drawTrace (traceY,color='green')
                            _judge(traceX,traceY,date)
                        })
                 })
                     .catch(function(error) {
                        alert("Can't connected to server!", error)
                    });
            });
      })
        .catch(function(error) {
          alert("Can't connected to server!", error)
        });;
}

function getActivityMacList(){
    let url="http://localhost:8010/proxy/floor/list"
    var request = new Request(url);
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                return data.data;
            });
      }).catch(function(error) {
          alert("Can't connected to server!", error)
        });
}

function getMacY(macX){
    var date = new Date();
    startTime=getTimeFromCurrent(10)
    endTime=getTimeFromCurrent(0)
    let url1="http://localhost:8010/proxy/device/trace?mac="+macX+"&start="+startTime+"&end="+endTime;
    //console.log(url1)
    let url2="http://localhost:8010/proxy/floor/list"
    //url1="http://localhost:8010/proxy/device/trace?mac=74:f6:1c:03:c3:a9&start=2020-04-15-16-00-00&end=2020-04-15-16-32-00";
    var request1 = new Request(url1);
    fetch(request1,{mode: 'cors'})
        .then(function(response1) {
            res1=response1.json();
            res1.then(
                data1=>{
                //console.log(data1)
                let traceX=data1.data[0].trace;
                //console.log(traceX)
                var request2 = new Request(url2);
                fetch(request2,{mode: 'cors'})
                    .then(function(response2) {
                      res2=response2.json();
                      res2.then(
                        data=>{
                            let collectionOfY=data.data;
                            drawTrace(traceX)
                            getDangerousMacY(collectionOfY,0,traceX,startTime,endTime,date,macX);
                        });
                  })
                    .catch(function(error) {
                      alert("Can't connected to server!", error)
                    });
            })
        })
        .catch(function(error) {
          alert("Can't connected to server!", error)
        });
}

function getDangerousMacY(collectionOfY,idx,traceX,startTime,endTime,date,macX){
    if(idx!=collectionOfY.length){
        //console.log("maxY:",collectionOfY[idx].mac);
        let url="http://localhost:8010/proxy/device/trace?mac="+collectionOfY[idx].mac+"&start="+startTime+"&end="+endTime;
        //console.log("url:",url)
        var request= new Request(url);
        let mode;
        if(idx==0) mode="start"
        else if(idx==collectionOfY.length-1) mode="end"
        else mode="batch"
        fetch(request,{mode: 'cors'})
        .then(function(response) {
            res=response.json();
            res.then(
                data=>{
                //console.log("183:",data)
                let traceY=data.data[0].trace;
                //console.log("185:",traceY)
                _judge(traceX,traceY,date,macX,collectionOfY[idx].mac,collectionOfY[idx].x,collectionOfY[idx].y,mode);
                getDangerousMacY(collectionOfY,idx+1,traceX,startTime,endTime,date,macX)
            })
        }).catch(function(error) {
          alert("Can't connected to server!", error)
        });
    }
}

function distance(x1,y1,x2,y2){
    return Math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
}

function showMacY(){
    let myTable = document.getElementById("myTable");
    var rowNum=myTable.rows.length;
     for (i=0;i<rowNum;i++)
     {
         myTable.deleteRow(i);
         rowNum=rowNum-1;
         i=i-1;
     }
    let macX=document.getElementById("macAddr").value
    getMacY(macX)
}

function _judge(traceX,traceY,date,macX,macY,x,y,mode="normal"){
    let i;
    let ret=[]
    if(mode=="start")
        document.getElementById("myLabel").innerText="正在查询..."
    else if(mode=="end")
        document.getElementById("myLabel").innerText="批量查询"
    //console.log("traceX:",traceX)
    //console.log("traceY:",traceY)
    if(traceY.length==0){
        ret=["Safe"]
    }
    else{
        for (i = 0; i < traceX.length; i++) {
            let point=traceX[i]
            if(Math.abs(point.step-traceY[0].step)<60)
                break
        }
        if(i==traceX.length)
            ret=["Safe"]
        else{
            let minLen=distance(traceX[i].x,traceX[i].y,traceY[0].x,traceY[0].y)
            let timeStep=traceX[i].step
            let minX=traceY[0].x
            let minY=traceY[0].y
            i=i+1
            let indexJ=1
            for (;i<traceX.length;i++,indexJ++){
                if(indexJ>=traceY.length)
                    break
                let curDis=distance(traceY[indexJ].x,traceY[indexJ].y,traceX[i].x,traceX[i].y)
                if(curDis<minLen){
                    minLen=curDis
                    timeStep=traceX[i].step
                    minX=traceY[indexJ].x
                    minY=traceY[indexJ].y
                }
            }
            if(minLen>10)
                ret=["Safe"]
            else{
                date.setSeconds(date.getSeconds()-600+timeStep)
                ret=[minLen,buildFormatTime(date,true),minX,minY]
            }
        }
    }
    if(mode=="start"){
        let myTable = document.getElementById("myTable");
        myTable.createCaption("可疑mac坐标")
        let newTr = myTable.insertRow(myTable.rows.length);
        newTr.insertCell().innerText="警报级别";
        newTr.insertCell().innerText="mac地址";
        newTr.insertCell().innerText="mac横坐标";
        newTr.insertCell().innerText="mac纵坐标";
        newTr.insertCell().innerText="时间";
        newTr.insertCell().innerText="与查询点距离";
    }
    if(mode=="end"){
        let myTable = document.getElementById("myTable");
        if(myTable.rows.length==1){
            myTable.deleteRow(0);
            let newTr = myTable.insertRow(myTable.rows.length);
            let newTd0 = newTr.insertCell();
            let newTd1 = newTr.insertCell();
            newTd0.style.background="#00FF7F";
            newTd1.innerText="恭喜，没有近距接触者！";
        }
    }
    if(ret.length==1){
        if(mode=="normal"){
            let myTable = document.getElementById("myTable");
            let newTr = myTable.insertRow(myTable.rows.length);
            let newTd0 = newTr.insertCell();
            let newTd1 = newTr.insertCell();
            newTd0.style.background="#00FF7F";
            newTd1.innerText="恭喜，没有近距接触者！";
        }
     }
    else{
        if(macX!=undefined&&macX==macY)
            return
        let myTable = document.getElementById("myTable");
        let newTr = myTable.insertRow(myTable.rows.length);
        if(ret[0]<5){
            newTr.insertCell().style.background="#DC143C";
            if(mode=="normal"){
                newTr.insertCell().innerText="危险:两个设备在"+ret[1]+"距离仅为"+ret[0].toFixed(3)+"m";
            }
            else{
                newTr.insertCell().innerText=macY;
                newTr.insertCell().innerText=ret[2].toFixed(3);
                newTr.insertCell().innerText=ret[3].toFixed(3);
                newTr.insertCell().innerText=ret[1];
                newTr.insertCell().innerText=ret[0].toFixed(3);
                drawPoint ([{x:ret[2].toFixed(3),y:ret[3].toFixed(3),color:"#DC143C"}])
            }
        }
        else{
            newTr.insertCell().style.background="#FFA500";
            if(mode=="normal"){
                newTr.insertCell().innerText="警报:两个设备在"+ret[1]+"距离为"+ret[0].toFixed(3)+"m";
            }
            else{
                newTr.insertCell().innerText=macY;
                newTr.insertCell().innerText=ret[2].toFixed(3);
                newTr.insertCell().innerText=ret[3].toFixed(3);
                newTr.insertCell().innerText=ret[1];
                newTr.insertCell().innerText=ret[0].toFixed(3);
                drawPoint ([{x:ret[2].toFixed(3),y:ret[3].toFixed(3),color:"#FFA500"}])
            }
        }
    }
}

function judge(){
    let myTable = document.getElementById("myTable");
    var rowNum=myTable.rows.length;
    for (i=0;i<rowNum;i++){
         myTable.deleteRow(i);
         rowNum=rowNum-1;
         i=i-1;
    }
    let mac1=document.getElementById("macAddr1").value
    let mac2=document.getElementById("macAddr2").value
    queryTraceFromMac(mac1,mac2)
}

function getTimeFromCurrent(timeInMinutes) {
    var date = new Date();
    date.setMinutes(date.getMinutes()-timeInMinutes)
    return buildFormatTime(date);
}

function buildFormatTime(date,flag){
    var strMonth = date.getMonth() + 1;
    var strDate = date.getDate();
    var strHour = date.getHours();
    var strMin = date.getMinutes();
    var strSec = date.getSeconds();
    if (strMonth >= 1 && strMonth <= 9) {
        strMonth = "0" + strMonth;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    if (strHour >= 0 && strHour <= 9) {
        strHour = "0" + strHour;
    }
    if (strMin >= 0 && strMin <= 9) {
        strMin = "0" + strMin;
    }
    if (strSec >= 0 && strSec <= 9) {
        strSec = "0" + strSec;
    }
    var currentdate;
    if(flag==true){
        currentdate= date.getFullYear() + '-'
            + strMonth + '-'
            + strDate + ' '
            + strHour + ':'
            + strMin + ':'
            + strSec;
    }
    else{
        currentdate= date.getFullYear() + '-'
                + strMonth + '-'
                + strDate + '-'
                + strHour + '-'
                + strMin + '-'
                + strSec;
    }
    return currentdate;
}

function ripple(dom,ev){
    //console.log(ev)
    var x = ev.offsetX;
    var y = ev.offsetY;
    dom.style.setProperty('--x',x+'px');
    dom.style.setProperty('--y',y+'px');
  }

function timeFormatter(time){
    let timeList=time.split('-');
    if(timeList.length==6)
        return timeList[0]+"-"+timeList[1]+"-"+timeList[2]+" "+timeList[3]+":"+timeList[4]+":"+timeList[5];
    else
        return timeList[0]+"-"+timeList[1]+"-"+timeList[2]+":"+timeList[3];
}

function initialize(pageNumber){
    let width="637.5px";
    let height="435px";
    d3.select("svg").remove()
    svg=d3.select("#myMap"+pageNumber)
                .append("svg")
                .attr("width", width)
                .attr("height", height)
    let myTable = document.getElementById("myTable1");
    var rowNum=myTable.rows.length;
    for (let i=0;i<rowNum;i++)
    {
         myTable.deleteRow(i);
         rowNum=rowNum-1;
         i=i-1;
    }
    myTable = document.getElementById("myTable2");
    rowNum=myTable.rows.length;
    for (let i=0;i<rowNum;i++)
    {
         myTable.deleteRow(i);
         rowNum=rowNum-1;
         i=i-1;
    }
}

function queryTwoMac(){
    let mac1=document.getElementById("macAddr1").value
    let mac2=document.getElementById("macAddr2").value
    let startTime=document.getElementById("Start_Time1").value //2020-04-25-19-40-00
    let endTime=document.getElementById("End_Time1").value //2020-04-25-19-45-00
    //startTime="2020-04-25-19-40-00"
    //endTime="2020-04-25-19-45-00"
    //mac1="01:27:ac:b0:4c:26"
    //mac2="51:2a:71:ad:d1:45"
    let url="http://localhost:8010/proxy/device/detection_single?start="+
    startTime+"&end="+endTime+"&mac="+mac1+"&target="+mac2;
    initialize("2");
    drawTrace(mac1,startTime,endTime)
    drawTrace(mac2,startTime,endTime,color='green')
    var request = new Request(url);
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                let detectRes=data.data;
                let alarmPos=[]
                for(let i=0;i<detectRes.length;++i){
                    if(detectRes[i].distance<=10)
                        alarmPos.push(detectRes[i])
                }
                if(alarmPos.length==0){
                    let th=["警报级别","详细信息"]
                    let myTable = document.getElementById("myTable2");
                    let newTr = myTable.insertRow(myTable.rows.length);
                    for(let i=0;i<th.length;++i){
                        let newTd=newTr.insertCell();
                        newTd.innerText=th[i];
                        newTd.style="font-weight:bold";
                    }

                    newTr = myTable.insertRow(myTable.rows.length);
                    newTd = newTr.insertCell();
                    newTd.innerText="安全";
                    newTd.style.color="#00CD00";
                    newTd.style.width="50%";
                    newTr.insertCell().innerText="恭喜,两个设备无近距离接触记录！";
                }
                else{
                    let th=["警报级别","时间","两个设备距离"]
                    let myTable = document.getElementById("myTable2");
                    let newTr = myTable.insertRow(myTable.rows.length);
                    for(let i=0;i<th.length;++i){
                        let newTd=newTr.insertCell();
                        newTd.innerText=th[i];
                        newTd.style="font-weight:bold";
                    }
                    for(let i=0;i<alarmPos.length;++i){
                        newTr = myTable.insertRow(myTable.rows.length);
                        if(alarmPos[i].distance<=5){
                            newTd = newTr.insertCell();
                            newTd.innerText="危险";
                            newTd.style.color="#DC143C";
                        }
                        else{
                            newTd = newTr.insertCell();
                            newTd.innerText="警报";
                            newTd.style.color="#EE7942";
                        }
                        newTr.insertCell().innerText=timeFormatter(alarmPos[i].eventTime);
                        newTr.insertCell().innerText=alarmPos[i].distance.toFixed(3)+"m";
                    }
                }
            });
      })
    .catch(function(error) {
      alert("Can't connected to server!", error)
    });
}

function detection(ret,start,end,macY,index,macX){
    let url="http://localhost:8010/proxy/device/detection_single?start="+
    start+"&end="+end+"&mac="+macY[index].DeviceMAC+"&target="+macX;
    var request = new Request(url);
    console.log(url)
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                console.log(data.data);
                if(data.data.length!=0){
                    let start=0;
                    while((start<data.data.length)&&(data.data[start].distance==null)){
                       console.log(data.data[start].distance)
                       start++;
                    }
                    if(start!=data.data.length){
                        let choose=start;
                        let minDis=data.data[start].distance;
                        for(let i=start+1;i<data.data.length;++i){
                            if(data.data[i].distance==null)
                                continue;
                            if(data.data[i].x==null)
                                continue;
                            if(data.data[i].y==null)
                                continue;
                            if(data.data[i].distance<minDis){
                                minDis=data.data[i].distance;
                                choose=i;
                            }
                        }
                        tmp=data.data[choose]
                        if(tmp.distance<=10){
                            tmp.mac=macY[index].DeviceMAC
                            ret.push(tmp);
                            if(tmp.distance<=5){
                                drawPoint ([{x:tmp.x,y:tmp.y,color:"#DC143C"}]);
                            }
                            else{
                                drawPoint ([{x:tmp.x,y:tmp.y,color:"#EE7942"}]);
                            }
                        }
                    }
                }
                if(index+1!=macY.length)
                    detection(ret,start,end,macY,index+1,macX);
                else
                    detection_show(ret);
            })})
}

function detection_show(alarmPos){
    console.log(alarmPos)
    if(alarmPos.length==0){
        let th=["警报级别","详细信息"]
        let myTable = document.getElementById("myTable1");
        let newTr = myTable.insertRow(myTable.rows.length);
        for(let i=0;i<th.length;++i){
            let newTd=newTr.insertCell();
            newTd.innerText=th[i];
            newTd.style="font-weight:bold";
        }

        newTr = myTable.insertRow(myTable.rows.length);
        newTd = newTr.insertCell();
        newTd.innerText="安全";
        newTd.style.color="#00CD00";
        newTd.style.width="50%";
        newTr.insertCell().innerText="恭喜,无近距离接触者！";
    }
    else{
        let th=["警报级别","可疑mac地址","可疑mac横坐标","可疑mac纵坐标","时间","两个设备距离"]
        let myTable = document.getElementById("myTable1");
        let newTr = myTable.insertRow(myTable.rows.length);
        for(let i=0;i<th.length;++i){
            let newTd=newTr.insertCell();
            newTd.innerText=th[i];
            newTd.style="font-weight:bold";
        }
        for(let i=0;i<alarmPos.length;++i){
            newTr = myTable.insertRow(myTable.rows.length);
            if(alarmPos[i].distance<=5){
                newTd = newTr.insertCell();
                newTd.innerText="危险";
                newTd.style.color="#DC143C";
                //drawPoint ([{x:alarmPos[i].x,y:alarmPos[i].y,color:"#DC143C"}]);
            }
            else{
                newTd = newTr.insertCell();
                newTd.innerText="警报";
                newTd.style.color="#EE7942";
                //drawPoint ([{x:alarmPos[i].x,y:alarmPos[i].y,color:"#EE7942"}]);
            }
            newTr.insertCell().innerText=alarmPos[i].mac;
            newTr.insertCell().innerText=alarmPos[i].x.toFixed(3);
            newTr.insertCell().innerText=alarmPos[i].y.toFixed(3);
            newTr.insertCell().innerText=timeFormatter(alarmPos[i].eventTime);
            newTr.insertCell().innerText=alarmPos[i].distance.toFixed(3)+"m";
        }
    }
}

function queryOneMac(){
    let mac=document.getElementById("macAddr").value
    let startTime=document.getElementById("Start_Time").value //2020-04-25-19-40-00
    let endTime=document.getElementById("End_Time").value //2020-04-25-19-45-00
    //startTime="2020-04-25-19-40-00"
    //endTime="2020-04-25-19-45-00"
    //mac="01:27:ac:b0:4c:26"
    //let url="http://localhost:8010/proxy/device/detection?start="+
    //startTime+"&end="+endTime+"&mac="+mac;
    let url="http://localhost:8010/proxy/device/neighbor?mac="+
    mac+"&start="+startTime+"&end="+endTime+"&limit=10&rssi=80"
    console.log(url)
    var request = new Request(url);
    initialize("1")
    drawTrace(mac,startTime,endTime)
    fetch(request,{mode: 'cors'})
        .then(function(response) {
          res=response.json();
          res.then(
            data=>{
                console.log(data.data);
                detection([],startTime,endTime,data.data,0,mac);
            }
          )
        }
    )
}