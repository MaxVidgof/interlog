import Component from './Component.js';
 
export default class Slider extends Component {
	constructor(onDeletePressed, onChange, type) {
		super();
		this.div = document.createElement('div');
		this.id = Date.now();
		this.div.setAttribute('id', this.id);
		this.root.appendChild(this.div);
		this.onChange = onChange
		this.deleteBtn = document.createElement('button');
		this.deleteBtn.innerText = '-';
		this.deleteBtn.addEventListener('click', () => {onDeletePressed(this);});
		this.div.appendChild(this.deleteBtn);
		this.leftInput = document.createElement('input');
		this.leftInput.required=true;
		if (type=="number") {
			this.leftInput.type = "number";
			this.leftInput.min = 0;
			this.leftInput.max = 1;
			this.leftInput.step = 0.01;
		} else if (type=="datetime-local") {
			this.leftInput.type = "datetime-local"
			this.leftInput.min = undefined;
		}
		this.leftInput.value = this.leftInput.min;
		this.div.appendChild(this.leftInput);
		this.rightInput = document.createElement('input');
		this.rightInput.required=true;
		if (type=="number") {
			this.rightInput.type = "number";
			this.rightInput.min = 0;
			this.rightInput.max = 1;
			this.rightInput.step = 0.01;
		} else if (type=="datetime-local") {
			this.rightInput.type = "datetime-local"
			this.rightInput.max = undefined;
		}
		this.rightInput.setAttribute('value', this.rightInput.max);
		this.div.appendChild(this.rightInput);
		// slider
		this.left = "";
		this.right = "";
		this.leftInput.addEventListener('input', (evt) => {this.left = this.leftInput.value});
		this.rightInput.addEventListener('input', (evt) => this.right = this.rightInput.value);
	}
 
	set left(val) {
		this.leftInput.value = val;
//		this.left = val;
		this.onChange()
		// slider
	}
 
	set right(val) {
		this.onChange()
		this.rightInput.value = val;
//		this.right = val;
		// slider
	}
 
}
