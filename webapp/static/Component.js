export default class Component {
	constructor(){
		this.root = document.createElement("div");
	}

	render(parent){
		if(parent!==undefined){
			parent.appendChild(this.root);
		}
		return this.root;
	}
}

