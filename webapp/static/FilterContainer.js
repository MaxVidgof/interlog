import Component from './Component.js';
import Filter from './Filter.js';

export default class FilterContainer extends Component{
	constructor(onApplyPushed, start, end){
		super()
		this.root.setAttribute('class', 'col-sm');
		this.onApplyPushed = onApplyPushed
		this.filterSettings = {
			filter1: [],
			filter2: [],
			filter3: [],
			filter4: [],
			filter5: [],
			filter5attribute: "Empty",
			visualization: "heu",
			distance: 0
		}
		this.filter1 = new Filter(this.setFilter1.bind(this), "Time filter", "datetime-local", "Time intervals", start, end);
		this.filter2 = new Filter(this.setFilter2.bind(this), "Variants filter", "number", "From least frequent (0) to most frequent (1)", 0, 1);
		this.filter3 = new Filter(this.setFilter3.bind(this), "Performance filter", "number", "From fastest (0) to slowest (1)", 0, 1);
		this.filter4 = new Filter(this.setFilter4.bind(this), "Activities filter", "number", "From least frequent (0) to most frequent (1)", 0, 1);
		this.filter5 = new Filter(this.setFilter5.bind(this), "Additional filter", "number", "Smallest existing value to largest if numeric; least frequent (0) to most frequent (1) if string", 0, 1 );


		this.viz = document.createElement("div");
		this.viz_head = document.createElement("h3");
		this.viz_head.innerText = "Select visualization";
		this.viz.appendChild(this.viz_head);
		this.viz.appendChild(document.createElement("br"));
		this.viz_dfgf = document.createElement("input");
		this.viz_dfgf.type="radio";
		this.viz_dfgf.name="viz";
		this.viz_dfgf.setAttribute('id', 'dfgf');
		this.viz.appendChild(this.viz_dfgf);
		this.l_dfgf = document.createElement("label");
		this.l_dfgf.setAttribute("for", "dfgf");
		this.l_dfgf.innerText = "Directly-follows-graph (frequency)";
		this.viz.appendChild(this.l_dfgf);
		this.viz.appendChild(document.createElement("br"));

		this.viz_dfgp = document.createElement("input");
		this.viz_dfgp.type="radio";
		this.viz_dfgp.name="viz";
		this.viz_dfgp.setAttribute('id', 'dfgp');
		this.viz.appendChild(this.viz_dfgp);
		this.l_dfgp = document.createElement("label");
		this.l_dfgp.setAttribute("for", "dfgp");
		this.l_dfgp.innerText = "Directly-follows-graph (performance)";
		this.viz.appendChild(this.l_dfgp);
		this.viz.appendChild(document.createElement("br"));

                this.viz_heu = document.createElement("input");
                this.viz_heu.type="radio";
		this.viz_heu.name="viz";
                this.viz_heu.setAttribute('id', 'heu');
		this.viz_heu.checked=true;
                this.viz.appendChild(this.viz_heu);
                this.l_heu = document.createElement("label");
                this.l_heu.setAttribute("for", "heu");
		this.l_heu.innerText = "Heuristics miner";
                this.viz.appendChild(this.l_heu);
		this.viz.appendChild(document.createElement("br"));

		this.lev = document.createElement("input")
		this.lev.type = "checkbox"
		this.lev.name = "lev"
		this.lev.setAttribute('id', 'lev')
		this.viz.appendChild(this.lev)
		this.l_lev = document.createElement("label");
		this.l_lev.setAttribute("for", "lev");
		this.l_lev.innerText = "Calculate Levenshtein's distance (may take around 2 minutes)";
		this.viz.appendChild(this.l_lev);
		this.viz.appendChild(document.createElement("br"));

//		this.loader = document.createElement("div");
//		this.loader.setAttribute('id', 'loader');
//		this.loader.style.display = "none";
//		this.viz.appendChild(this.loader);

		this.applyBtn = document.createElement("button");
		this.applyBtn.innerText = "Apply";
		this.applyBtn.setAttribute('class', 'btn btn-primary')
		this.applyBtn.addEventListener('click', () => {
//			let data = new FormData();
//let filters = document.getElementsByClassName("filter");
//let filtersOk = true;
//for (filter of filters) {
//     for (let i = 2; i < filter.children.length; i = i+1)
//        if (!(filter.children[i].children[1].value <= filter.children[i].children[2].value)) {filtersOk = false}
//    for (i = 2; i < filter.children.length -1; i = i + 1){
//        if (!(filter.children[i].children[2].value <= filter.children[i+1].children[1].value)) {filtersOk = false}
//    }
//}
//if (filtersOk) {
document.getElementById("loader").style.display = "block";
if (this.viz_dfgf.checked) {
	this.filterSettings.visualization = "dfgf";
} else if (this.viz_dfgp.checked) {
	this.filterSettings.visualization = "dfgp";
} else {
	this.filterSettings.visualization = "heu;"
}
if (document.getElementById('lev').checked) {
	this.filterSettings.distance = 1
} else {
	this.filterSettings.distance = 0
}
this.filterSettings.filter5attribute = document.getElementsByTagName('select')[0].value
let data = JSON.stringify(this.filterSettings)
//                data.append('input_log_file', input.files[0])
	                fetch("https://interlog.cluster.ai.wu.ac.at/apply", {method: 'POST', body: data}).then((response => {return response.json()})).then((data) => {
//console.log(data)
				if (data.status && data.status==="expired"){ alert("Session expired. Please reload the page.");}
				if (data.error) {
					document.getElementById("loader").style.display = "none";
					alert("Error: "+data.error);
				}
				console.log("Time filter: " + data.time + " seconds")
				console.log("Variants filter: " + data.variants + " seconds")
				console.log("Performance filter: " + data.performance + " seconds")
				console.log("Activities filter: " + data.activities + " seconds")
				document.getElementById('model_1').children[0].children[0].innerText = "Traces: "+data.traces[0]
				document.getElementById('model_2').children[0].children[0].innerText = "Traces: "+data.traces[1]
				document.getElementById("loader").style.display = "none";
				console.log("Average Levenshtein's distance: "+data.distance)
				if (data.distance !== "null") {
					document.getElementById('lev_disp').style.display='block'
					document.getElementById('lev_disp').innerText="Average Levenshtein's distance: "+data.distance
				} else {
					document.getElementById('lev_disp').style.display='none'
					document.getElementById('lev_disp').innerText=''
				}
				onApplyPushed("applied");
			});
//			fetch().then(() => {onApplyPushed()});
//} else {
//	alert("Wrong filter settings!");
//}
console.log(this.filterSettings)
		})
//this.root.appendChild(this.filterX.render())
		//
		this.filters = document.createElement('div')
		this.root.appendChild(this.filters)
		this.root.appendChild(this.viz)
		this.root.appendChild(this.applyBtn)

		this.lev_disp = document.createElement('p')
		this.lev_disp.setAttribute('id', 'lev_disp')
		this.lev_disp.style.display = 'none'
		this.root.appendChild(this.lev_disp)
	}

	setFilter1(intervals){
		this.filterSettings.filter1 = intervals
	}
	setFilter2(intervals){
		this.filterSettings.filter2 = intervals
	}
	setFilter3(intervals){
		this.filterSettings.filter3 = intervals
	}
	setFilter4(intervals){
		this.filterSettings.filter4 = intervals
	}
	setFilter5(intervals){
		this.filterSettings.filter5 = intervals
	}

	render(parent){
		super.render(parent)
		this.filter1.render(this.filters)
		this.filter2.render(this.filters)
		this.filter3.render(this.filters)
		this.filter4.render(this.filters)
		this.filter5.render(this.filters)
	}
}
