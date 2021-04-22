import ModelContainer from './ModelContainer.js';
import FilterContainer from './FilterContainer.js';
import Component from './Component.js';

const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-img");


const baseUrl = document.getElementById("baseUrl").value;
const button = document.getElementById("upload_btn");
const input = document.getElementById("log_file");
button.addEventListener("click", () => {
	if(input.files.length>0){
		let data = new FormData()
		data.append('input_log_file', input.files[0])
		fetch("https://cherry-picker.cluster.ai.wu.ac.at/upload", {method: 'POST', body: data}).then((response) => {return response.json()}).then((data) => {

if (data.status && data.status==="expired"){ window.location.reload(); }

let root = document.getElementById("root");

const m0 = new ModelContainer(baseUrl, 0);

let rightPart = new Component()
rightPart.root.setAttribute('class', 'col-sm');

let start = new Date(data.start_time).toISOString().split("+")[0].split("Z")[0].split(".")[0].replace("T"," ")
let end = new Date(data.end_time).toISOString().split("+")[0].split("Z")[0].split(".")[0].replace("T", " ")

const f = new FilterContainer(() => {m1.render(rightPart.root); m2.render(rightPart.root)}, start, end);

//f.filter1.min = new Date(data.start_time).toISOString().split("Z")[0]
//f.filter1.max = new Date(data.end_time).toISOString().split("Z")[0]

//Proper setting of times:
f.filter1.sliders[0].leftInput.value = start
f.filter1.sliders[0].rightInput.value = end

//f.filter1.sliders[0].leftInput.value = "2012-01-01T00:00"


//for (let item of document.getElementsByClassName("datetimeInput")){
//	AnyTime.picker( item.id, { format: "%Y-%m-%dT%H:%i:%s%:", firstDOW: 1 } );
//}

const m1 = new ModelContainer(baseUrl, 1);
const m2 = new ModelContainer(baseUrl, 2);


m0.render(root);
f.render(root);
rightPart.render(root);

m1.render(rightPart.root);
m2.render(rightPart.root);

document.getElementById('model_0').children[0].children[0].innerText = "Traces: "+data.traces_u
console.log(data.start_time);
console.log(data.end_time);

document.getElementById('upload').remove()
let span = document.getElementsByClassName("close")[0];
// When the user clicks on <span> (x), close the modal
span.onclick = function() {
	modal.style.display = "none";
}
//document.getElementsByTagName("img").then((collection) => {
for (let image of document.getElementsByTagName("img")) {
	if (image.id !== "modal-img") {
		image.onclick = function(){
			modal.style.display = "block";
			modalImg.src = image.src;
		}
	}
}
		});
	}
} );
