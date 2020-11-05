import Component from './Component.js';

export default class ModelContainer extends Component{
	constructor(baseUrl, index){
		super()
		this.img = document.createElement("img")
		this.img_src = `${baseUrl}_l${index}.png`
		this.img.src = this.img_src
		this.downloadBtn = document.createElement("a")
		this.downloadBtn.innerText = "download log"
		this.downloadBtn.href = `${baseUrl}_l${index}.xes`
		this.downloadBtn.download = `l${index}.xes`

		this.root.appendChild(this.img)
		this.root.appendChild(this.downloadBtn)
	}

	render(parent){
		this.img.src = this.img_src + "?random="+new Date().getTime();
		return super.render(parent)
	}
}
