//TODO:执行js文件时的html代码中没有queryform，和控制台的html不同
let btn = document.createElement("button");
btn.innerHTML = "Apply";
btn.id = "mybtn";
btn.onclick = function AddBtn() {
    let btn = document.createElement('button');
    btn.innerHTML = "Automate";
    btn.onclick = function apply() {
        let form = null;
        let form_list = document.getElementsByTagName('form');
        for (let i = 0; i < form_list.length; i++) {
            let form_content = form_list[i].getElementsByTagName('select');
            if (form_content.length < 5) {
                continue;
            }
            form = form_content[i];
        }
        form = document.getElementById('queryform');
        if (form == null) { console.log("Not Found form"); return; }
        let list = form.getElementsByTagName('select');
        for (let i = 0; i < list.length; i++) { list[i].options[1].selected = true; list[i].onchange(); }
    };
    let menus = document.getElementById('menus');
    let li = document.createElement('li');
    li.appendChild(btn);
    menus.appendChild(li);
};
btn.className = "tooltip-tip ajax-load";
let menus = document.getElementById('menus');
let li = document.createElement('li');
li.appendChild(btn);
menus.appendChild(li);
form = document.getElementById('queryform')
list = form.getElementsByTagName('select')
for (var i = 0; i < list.length; i++) { list[i].options[1].selected = true; list[i].onchange(); }
