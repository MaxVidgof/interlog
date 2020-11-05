import ModelContainer from './ModelContainer.js';
import FilterContainer from './FilterContainer.js';

const baseUrl = document.getElementById("baseUrl").value;
const button = document.getElementById("upload_btn");
const input = document.getElementById("log_file");
button.addEventListener("click", () => {
	if(input.files.length>0){
		let data = new FormData()
		data.append('input_log_file', input.files[0])
		fetch("http://10.139.167.139:8000/upload", {method: 'POST', body: data}).then((response) => {return response.json()}).then((data) => {

let root = document.getElementById("root");
const m0 = new ModelContainer(baseUrl, 0);
const f = new FilterContainer(() => {m1.render(root); m2.render(root)});

//f.filter1.min = new Date(data.start_time).toISOString().split("Z")[0]
//f.filter1.max = new Date(data.end_time).toISOString().split("Z")[0]

//Proper setting of times:
//f.filter1.sliders[0].leftInput.value = new Date(data.start_time).toISOString().split("Z")[0]
//f.filter1.sliders[0].rightInput.value = new Date(data.end_time).toISOString().split("Z")[0]

f.filter1.sliders[0].leftInput.value = "2012-01-01T00:00"

f.render(root);

const m1 = new ModelContainer(baseUrl, 1);
const m2 = new ModelContainer(baseUrl, 2);

m0.render(root);
m1.render(root);
m2.render(root);

console.log(data.start_time);
console.log(data.end_time);

document.getElementById('upload').remove()
		});
	}
} );
