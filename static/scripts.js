//javascript-only elements
const image_check = document.getElementById("image_check");
const grid_check = document.getElementById("grid_check");
const mask_check = document.getElementById("mask_check");
const zoom_slider = document.getElementById("zoom_slider");
const x_slider = document.getElementById("x_slider");
const y_slider = document.getElementById("y_slider");
const image_board = document.getElementById("image_board");

//enable elements
image_check.style.display="block";
grid_check.style.display="block";
mask_check.style.display="block";
zoom_slider.style.display="block";
x_slider.style.display="block";
y_slider.style.display="block";

//image toggle function

image_check.onclick=toggle_vis(this);
grid_check.onclick=toggle_vis(this);
mask_check.onclick=toggle_vis(this);

//zoom function
let zoom = 1; //default zoom
const zoom_interval = 0.1;

//by mouse wheel
document.addEventListener("wheel", function(e) {  
    if(e.deltaY > 0){    
		zoom += zoom_interval;
    }else{    
		zoom -= zoom_interval;
	}
        image_board.style.scale = zoom;
        zoom_slider.value = zoom;
});

//by slider

zoom_slider.oninput = slide_zoom(this);

/*

		dragElement(document.getElementById("image_board"));

		function dragElement(elmnt) {
			var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
			if (document.getElementById(elmnt.id + "header")) {
				// if present, the header is where you move the DIV from:
				document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
			} else {
			// otherwise, move the DIV from anywhere inside the DIV:
			elmnt.onmousedown = dragMouseDown;
		}

		function dragMouseDown(e) {
		e = e || window.event;
		e.preventDefault();
		// get the mouse cursor position at startup:
		pos3 = e.clientX;
		pos4 = e.clientY;
		document.onmouseup = closeDragElement;
		// call a function whenever the cursor moves:
		document.onmousemove = elementDrag;
		}

		function elementDrag(e) {
		e = e || window.event;
		e.preventDefault();
		// calculate the new cursor position:
		pos1 = pos3 - e.clientX;
		pos2 = pos4 - e.clientY;
		pos3 = e.clientX;
		pos4 = e.clientY;
		// set the element's new position:
		elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
		elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
		}

		function closeDragElement() {
		// stop moving when mouse button is released:
		document.onmouseup = null;
		document.onmousemove = null;
		}
		}
*/