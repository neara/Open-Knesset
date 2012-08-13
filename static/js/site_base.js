console.log(" in site base js start ");

var path = window.location.pathname;
console.log(path);

var u = encodeURIComponent('http://dev.oknesset.org' + path);

var xhr = new XMLHttpRequest();
xhr.open("GET", 'http://dev.oknesset.org' + path, true);
xhr.onreadystatechange = function(){
	if (xhr.readyState==4 && xhr.status==200){
		alert('success');
	}
};

xhr.send();
