const protocol="http"
const server=protocol+"://"+window.location.host;

function deactivate_button(btn){
    var btn=document.getElementById(btn);
    btn.disabled=true;
}

function activate_button(btn){
    var btn=document.getElementById(btn);
    btn.disabled=false;
}

function go_to_page(target){
    window.location.href=target;
}

function post_to_page(target){
    var form=document.createElement("form");
    document.body.appendChild(form);
    form.method="post";
    form.action=target;
    form.submit();
}

function go_to_login(){
    go_to_page(server+"/login");
}

function go_to_register(){
    go_to_page(server+"/register");
}

function go_to_dialog(){
    go_to_page(server+"/dialog");
}

function go_to_account(){
    go_to_page(server+"/account");
}

function set_input_invalid(id){
    var input=document.getElementById(id);
    input.classList.remove("is-valid");
    input.classList.add("is-invalid");
}

function set_input_valid(id){
    var input=document.getElementById(id);
    input.classList.remove("is-invalid");
    input.classList.add("is-valid");
}


function clear_input_invalid(id){
    var input=document.getElementById(id);
    input.classList.remove("is-invalid");
}

function set_text(id,text){
    var label=document.getElementById(id);
    label.innerHTML=text;
}

function set_error_text(id,error){
    var label=document.getElementById(id);
    label.classList.add("invalid-feedback");
    label.innerHTML=error;
}

function clear_error_text(id){
    var label=document.getElementById(id);
    label.classList.remove("invalid-feedback");
    label.innerHTML="";
}

function set_email_invalid(text){
    set_input_invalid("email");
    set_error_text("email-help",text);
}

function set_email_invalid_by_id(text,email_id){
    set_input_invalid(email_id);
    set_error_text(email_id+"-help",text);
}

function set_email_valid(){
    set_input_valid("email");
    clear_error_text("email-help");
}

function set_email_valid_by_id(email_id){
    set_input_valid(email_id);
    clear_error_text(email_id+"-help");
}

function set_password_invalid(id,text){
    set_input_invalid(id);
    set_error_text(id+"-help",text);
}

function set_password_valid(id){
    set_input_valid(id);
    clear_error_text(id);
}

function check_email_format(event){
    var email=document.getElementById("email").value;
    var suffix=email.split(".")
    if(email==""){
        if(event){
            set_email_invalid("邮箱不能为空");
        }
        return false;
    }
    if(email.search("@")==-1 || suffix.length==1){
        if(event){
            set_email_invalid("邮箱格式错误");
        }
        return false;
    }
    for(let s of suffix){
        if(s==""){
            if(event){
                set_email_invalid("邮箱格式错误");
            }
            return false;
        }
    }
    if(event){
        set_email_valid();
    }
    return true;
}

function check_email_format_by_id(event,email_id){
    var email=document.getElementById(email_id).value;
    var suffix=email.split(".")
    if(email==""){
        if(event){
            set_email_invalid_by_id("邮箱不能为空",email_id);
        }
        return false;
    }
    if(email.search("@")==-1 || suffix.length==1){
        if(event){
            set_email_invalid_by_id("邮箱格式错误",email_id);
        }
        return false;
    }
    for(let s of suffix){
        if(s==""){
            if(event){
                set_email_invalid_by_id("邮箱格式错误",email_id);
            }
            return false;
        }
    }
    if(event){
        set_email_valid_by_id(email_id);
    }
    return true;
}

function check_password_format(event){
    var password=document.getElementById("password").value;
    const legal="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&"
    if(password.length<8){
        if(event){
            set_password_invalid("password","密码过短。");
        }
        return false;
    }
    if(password.length>20){
        if(event){
            set_password_invalid("password","密码过长。");
        }
        return false;
    }
    for(let char of password){
        if(legal.indexOf(char)==-1){
            if(event){
                set_password_invalid("password","非法字符。")
            }
            return false;
        }
    }
    if(event){
        set_password_valid("password");
    }
    return true;
}

function check_password_format_by_id(event,password_id){
    var password=document.getElementById(password_id).value;
    const legal="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&"
    if(password.length<8){
        if(event){
            set_password_invalid(password_id,"密码过短。");
        }
        return false;
    }
    if(password.length>20){
        if(event){
            set_password_invalid(password_id,"密码过长。");
        }
        return false;
    }
    for(let char of password){
        if(legal.indexOf(char)==-1){
            if(event){
                set_password_invalid(password_id,"非法字符。")
            }
            return false;
        }
    }
    if(event){
        set_password_valid(password_id);
    }
    return true;
}

function check_password_again_format(event){
    var password=document.getElementById("password").value;
    var password_again=document.getElementById("password-again").value;
    // var legal="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&"
    if(password==""){
        if(event){
            set_password_invalid("password-again","请先设置密码。");
        }
        return false;
    }
    if(check_password_format(false)==false){
        if(event){
            set_password_invalid("password-again","设置的密码不符合安全规则。");
        }
        return false;
    }
    if(password!=password_again){
        if(event){
            set_password_invalid("password-again","两次输入的密码不相同。");
        }
        return false;
    }
    if(event){
        set_password_valid("password-again");
    }
    return true;
}

function check_password_again_format_by_id(event,password_id){
    var password=document.getElementById(password_id).value;
    var password_again=document.getElementById(password_id+"-again").value;
    // var legal="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&"
    if(password==""){
        if(event){
            set_password_invalid(password_id+"-again","请先设置密码。");
        }
        return false;
    }
    if(check_password_format_by_id(false,password_id)==false){
        if(event){
            set_password_invalid(password_id+"-again","设置的密码不符合安全规则。");
        }
        return false;
    }
    if(password!=password_again){
        if(event){
            set_password_invalid(password_id+"-again","两次输入的密码不相同。");
        }
        return false;
    }
    // if(password.length<8){
    //     set_password_invalid("password-again","密码过短。");
    //     return;
    // }
    // if(password.length>20){
    //     set_password_invalid("password-again","密码过长。");
    //     return;
    // }
    // for(let char of password){
    //     if(legal.search(char)==-1){
    //         set_password_invalid("password-again","非法字符。")
    //         return;
    //     }
    // }
    if(event){
        set_password_valid(password_id+"-again");
    }
    return true;
}

function check_create_button(email_id,password_id){
    if(check_email_format_by_id(false,email_id)&&check_password_format_by_id(false,password_id)&&check_password_again_format_by_id(false,password_id)){
        activate_button("btn-create");
    }
    else{
        deactivate_button("btn-create");
    }
}

function check_register_button(){
    if(check_email_format()&&check_password_format()&&check_password_again_format()){
        activate_button("btn-register");
    }
    else{
        deactivate_button("btn-register");
    }
}

function check_confirm_button(){
    if(check_email_format()){
        activate_button("btn-confirm");
    }
    else{
        deactivate_button("btn-confirm");
    }
}

function check_submit_button(){
    if(check_password_format()&&check_password_again_format()){
        activate_button("btn-submit");
    }
    else{
        deactivate_button("btn-submit");
    }
}

function on_gender_toggle(selectedId) {
    const male=document.getElementById("gender-male");
    const female=document.getElementById("gender-female");
    const hidden=document.getElementById("gender");

    if(selectedId === "gender-male"&&male.checked){
            female.checked=false;
    }
    if(selectedId === "gender-female"&&female.checked){
        male.checked=false;
    }

    if(male.checked){
        hidden.value="male";
    }
    else if(female.checked){
        hidden.value="female";
    }
    else{
        hidden.value="";
    }
}

function escape_html(text){
    var map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
    };
    return String(text).replace(/[&<>"']/g, function(m){ return map[m]; });
}

function render_markdown(mdText){
    // 如果 markdown 库没加载，安全显示文本
    if(!(window.marked && window.DOMPurify)){
        return escape_html(mdText).replace(/\n/g, "<br>");
    }
    var html = marked.parse(mdText, { gfm: true, breaks: true });
    return DOMPurify.sanitize(html);
}

function render_history(){
    const history_raw = document.getElementById("history-items-json").textContent.trim();
    const history_items = history_raw ? JSON.parse(history_raw) : [];
    const box = document.getElementById("history");

    if (!history_items || history_items.length === 0){
        box.innerHTML = "<b>暂无历史记录</b>";
        return;
    }

    let html = "";
    for (const item of history_items){
        html += `
            <div class="history-item">
                <div class="history-time">${escape_html(item.time || "")}</div>
                <div class="history-question"><b>您：</b>${escape_html(item.question || "")}</div>
                <div class="history-answer">
                    <b>智能问答系统：</b>
                    <article class="markdown-body">
                        ${render_markdown(item.answer || "")}
                    </article>
                </div>
            </div>
        `;
    }

    box.innerHTML = html;
}

function register_request(){
    var xhttp=new XMLHttpRequest();
    var email=document.getElementById("email").value;
    var password=document.getElementById("password").value;
    var password_again=document.getElementById("password-again").value;
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                alert(response["content"]);
            }
            else if(response["type"]=="url"){
                alert("注册成功。")
                go_to_page(server+response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/register",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("email="+email+"&password="+password+"&password_again="+password_again);
}

function create_request(){
    var xhttp=new XMLHttpRequest();
    var email=document.getElementById("email-1").value;
    var password=document.getElementById("password-1").value;
    var password_again=document.getElementById("password-1-again").value;
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                alert(response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/account/create",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("email="+email+"&password="+password+"&password_again="+password_again);
}

function login_request(){
    var xhttp=new XMLHttpRequest();
    var email=document.getElementById("email").value;
    var password=document.getElementById("password").value;
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                if(response["id"]=="email"){
                    set_email_invalid(response["content"]);
                }
                else if(response["id"]=="password"){
                    set_password_invalid(response["id"],response["content"]);
                }
            }
            else if(response["type"]=="url"){
                go_to_page(server+response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/login",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("email="+email+"&password="+password);
}

function forget_request(){
    var xhttp=new XMLHttpRequest();
    var email=document.getElementById("email").value;
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                alert(response["content"]);
            }
            else if(response["type"]=="url"){
                alert("请留意您的邮箱，我们的管理员将把重置后的密码发送到您的邮箱中。")
                go_to_page(server+response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/forget",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("email="+email);
}

function dialog_request(){
    var d=new Date();
    var time=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate()+" "+d.getHours()+":"+d.getMinutes()+":"+d.getSeconds();
    var question=document.getElementById("question-text").value;
    if(question==""){
        return;
    }

    var answer_head=document.getElementById("answer-head");
    var spin=document.createElement("div");
    spin.setAttribute("class","spinner-border float-end spinner");
    spin.setAttribute("role","status");
    spin.setAttribute("id","spin");
    answer_head.appendChild(spin);

    var answer=document.getElementById("answer");
    answer.innerHTML=escape_html(time)+"<br><b>您：</b>"+escape_html(question)+"<br>";

    var xhttp=new XMLHttpRequest();
    xhttp.timeout=120000;
    xhttp.ontimeout=function(){
        var s=document.getElementById("spin");
        if(s){ answer_head.removeChild(s); }
        alert("网络连接超时。");
    };
    xhttp.onerror=function(){
        var s=document.getElementById("spin");
        if(s){ answer_head.removeChild(s); }
        alert("您的网络似乎出现了一些问题。");
    };
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            var s=document.getElementById("spin");
            if(s){ answer_head.removeChild(s); }

            if(response["type"]=="info"){
                alert(response["content"]);
            }
            else if(response["type"]=="url"){
                go_to_page(response["url"]);
            }
            else if(response["type"]=="answer"){
                var rendered=render_markdown(response["content"]);
                answer.innerHTML += "<b>智能问答系统：</b><article class='markdown-body'>"+rendered+"</article>";
            }
        }
    };
    xhttp.open("POST",server+"/do/dialog",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("time="+encodeURIComponent(time)+"&question="+encodeURIComponent(question));
}

// function dialog_request(){
//     var d=new Date();
//     time=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate()+" "+d.getHours()+":"+d.getMinutes()+":"+d.getSeconds();
//     var question=document.getElementById("question-text").value;
//     if(question==""){
//         return;
//     }
//     var answer_head=document.getElementById("answer-head");
//     var spin=document.createElement("div");
//     spin.setAttribute("class","spinner-border float-end spinner");
//     spin.setAttribute("role","status");
//     spin.setAttribute("id","spin");
//     answer_head.appendChild(spin);
//     var answer=document.getElementById("answer");
//     answer.innerHTML=time+"<br><b>您：</b>"+question+"<br>";
//     var xhttp=new XMLHttpRequest();
//     //! 
//     xhttp.timeout=120000;
//     xhttp.ontimeout=function(){
//         answer_head.removeChild(document.getElementById("spin"));
//         alert("网络连接超时。");
//     }
//     xhttp.onerror=function(){
//         answer_head.removeChild(document.getElementById("spin"));
//         alert("您的网络似乎出现了一些问题。");
//     }
//     xhttp.onreadystatechange=function(){
//         if(this.readyState==4&&this.status==200){
//             var response=JSON.parse(this.response);
//             if(response["type"]=="info"){
//                 answer_head.removeChild(document.getElementById("spin"));
//                 alert(response["content"]);
//             }
//             else if(response["type"]=="url"){
//                 go_to_page(response["url"]);
//             }
//             else if(response["type"]=="answer"){
//                 answer.innerHTML+=response["content"];
//                 answer_head.removeChild(document.getElementById("spin"));
//             }
//         }
//     }
//     xhttp.open("POST",server+"/do/dialog",true);
//     xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
function change_body_request() {
    var gender = document.getElementById("gender").value;
    var age = document.getElementById("age").value;
    var height = document.getElementById("height").value;
    var weight = document.getElementById("weight").value;
    var fpg = document.getElementById("fpg").value;
    var ogtt = document.getElementById("ogtt").value;
    var hba1c = document.getElementById("hba1c").value;

    var xhttp = new XMLHttpRequest();
    xhttp.timeout = 4000;
    xhttp.ontimeout = function() {
        alert("网络连接超时。");
    }
    xhttp.onerror = function() {
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.response);
            if (response["type"] == "info") {
                alert(response["content"]);
            } else if (response["type"] == "url") {
                alert("保存成功！");
                go_to_page(server + response["content"]);
            } else {
                alert("保存成功！");
            }
        }
    }
    xhttp.open("POST", server + "/do/body/change", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var params = "gender=" + gender + 
                 "&age=" + age + 
                 "&height=" + height + 
                 "&weight=" + weight + 
                 "&fpg=" + fpg + 
                 "&ogtt=" + ogtt + 
                 "&hba1c=" + hba1c;
                 
    xhttp.send(params);
}

function change_password_request(admin=false){
    var password=document.getElementById("password").value;
    var password_again=document.getElementById("password-again").value;
    if(admin){
        var email=document.getElementById("email").value;
    }
    var xhttp=new XMLHttpRequest();
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                alert(response["content"]);
            }
            else if(response["type"]=="url"){
                alert("修改密码成功，请重新登陆。");
                go_to_login();
            }
            else{
                alert("网络出现错误，修改密码失败，请重新登录。");
                go_to_login();
            }
        }
    }
    xhttp.open("POST",server+"/do/account/change",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    if(admin){
        xhttp.send("email="+email+"&password="+password+"&password_again="+password_again);
    }
    else{
        xhttp.send("password="+password+"&password_again="+password_again);
    }
}

function ban_request(){
    var email=document.getElementById("email-2").value;
    var xhttp=new XMLHttpRequest();
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            console.log(response);
            if(response["type"]=="info"){
                if(response["id"]=="alert"){
                    alert(response["content"]);
                }
                else{
                    set_input_invalid(response["id"]);
                    set_error_text(response["id"]+"-help",response["content"]);
                }
            }
            else if(response["type"]=="url"){
                go_to_page(response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/account/ban",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("type=ban"+"&email="+email);
}

function unban_request(){
    var email=document.getElementById("email-2").value;
    var xhttp=new XMLHttpRequest();
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"){
                if(response["id"]=="alert"){
                    alert(response["content"]);
                }
                else{
                    set_input_invalid(response["id"]);
                    set_error_text(response["id"]+"-help",response["content"]);
                }
            }
            else if(response["type"]=="url"){
                go_to_page(response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/account/ban",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("type=unban"+"&email="+email);
}

function read_message_request(idx){
    var xhttp=new XMLHttpRequest();
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="info"&&response["content"]=="success"){
                var p=document.getElementById("p-"+idx)
                p.removeChild(document.getElementById("btn-read-"+idx));
                p.innerHTML="<span class='read'>已读</span>";
            }
            else if(response["type"]=="url"){
                go_to_page(response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/account/message",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("idx="+idx);
}

function graph_request(){
    var name=document.getElementById("search").value
    var xhttp=new XMLHttpRequest();
    xhttp.timeout=4000;
    xhttp.ontimeout=function(){
        alert("网络连接超时。");
    }
    xhttp.onerror=function(){
        alert("您的网络似乎出现了一些问题。");
    }
    xhttp.onreadystatechange=function(){
        if(this.readyState==4&&this.status==200){
            var response=JSON.parse(this.response);
            if(response["type"]=="data"){
                visualization(response["content"]);
            }
            else if(response["type"]=="url"){
                go_to_page(response["content"]);
            }
        }
    }
    xhttp.open("POST",server+"/do/graph",true);
    xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhttp.send("name="+name);
}