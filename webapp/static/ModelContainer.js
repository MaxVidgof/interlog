import Component from './Component.js';

export default class ModelContainer extends Component{
	constructor(baseUrl, index){
		super()
//                this.div = document.createElement('div');
		if (index===0) {this.root.setAttribute('class', 'col-sm')}
		this.root.setAttribute('id', `model_${index}`);
		this.img = document.createElement("img")
		this.img_src = `${baseUrl}_l${index}.png`
		this.img.src = this.img_src
		this.img.alt = "Mined model"
		this.top = document.createElement("div")
		this.traceNumber = document.createElement("p")
		this.traceNumber.innerText = "Traces: "
		this.traceNumber.setAttribute('class', 'text-left float-left')
		this.downloadBtn = document.createElement("a")
		this.downloadBtn.innerText = "download log"
		this.downloadBtn.href = `${baseUrl}_l${index}.xes`
		this.downloadBtn.download = `l${index}.xes`
		this.downloadBtn.setAttribute('class', 'btn btn-light float-right');

		this.top.appendChild(this.traceNumber)
		this.top.appendChild(this.downloadBtn)
		this.root.appendChild(this.top)
		this.root.appendChild(this.img)
//		this.root.appendChild(this.div)
	}

	render(parent){
		this.img.src = this.img_src + "?random="+new Date().getTime();
		return super.render(parent)
	}
}
