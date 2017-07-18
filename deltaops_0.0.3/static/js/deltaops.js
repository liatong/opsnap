

//Show table function 
    function showDataTable(tb,obj,stdhtml,endtdhtml,bindfunc){
        
        var rt = 1;
        tb.children().remove();
        if(typeof obj != "undefined" && typeof obj == "object" && typeof tb == "object"){
            $.each(obj,function(key,value){
                var itr = document.createElement('tr');
                //create tr fist td,if have stdhtml
                if( typeof stdhtml == 'string'){
                    var std = document.createElement('td');
                    std.innerHTML = stdhtml;
                    itr.appendChild(std);
                }
                value.map(function(text){
                    var btd = document.createElement('td');
                    btd.innerText= text;
                    itr.appendChild(btd);
                });
                // create define td when have stdhtml
                if( typeof endtdhtml == 'string'){
                    var endtd = document.createElement('td');
                    endtd.innerHTML = endtdhtml;
                    itr.appendChild(endtd);
                }
                
                //append tr to tbody
                tb.append(itr);
            });
            
            //  callback append html even function
            if( typeof bindfunc == "function" ){
                bindfunc();
            };
            rt = 1;
            
        }else{
            console.log('show table is obj is undefine.');
            rt = 0;
        }
        console.log('debug');
        return rt;
        
    }
    
    
// Up page and down page , must have getTableData function to get data from server api and display the data to html:table;
     
    $("#upPage").click(function(){
        
        if($("#pageNum").text() != '1'){
            $("#pageNum").text(parseInt($("#pageNum").text())-1);
            console.log($("#pageNum").text());
            getTableData();
        }
    })
    $("#downPage").click(function(){
        $("#pageNum").text(parseInt($("#pageNum").text())+1);
        getTableData();
    })
   function getCookie(name)//取cookies函数        
    {
        var arr = document.cookie.match(new RegExp("(^| )"+name+"=([^;]*)(;|$)"));
         if(arr != null) return unescape(arr[2]); return null;

    }
    name = getCookie('username');
    FistName = name.split("\"")[1].split("@")[0];
    $("#login-user").text(FistName);
    
    
    