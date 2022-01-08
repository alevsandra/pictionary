//setting countdown
let seconds = 30;
//countdown function
var x = setInterval(function onTimer() {
    //updating clock
    document.getElementById('count_down').innerHTML = 0 + " : " + seconds;
    seconds--;
    //when countdown ends
    if (seconds < 0) {
        clearInterval(x);
    }
}, 1000);

//initializing canvas
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext("2d");

//function to set up brush color
function color(color_value) {
        ctx.strokeStyle = color_value;
        ctx.fillStyle = color_value;
}

window.addEventListener('load', () => {

    //canvas size
    ctx.canvas.height = 0.65 * window.innerHeight;
    //mobile
    if (window.innerHeight > window.innerWidth) ctx.canvas.width = 0.90 * window.innerWidth;
    //desktop
    else ctx.canvas.width = 0.60 * window.innerWidth;

    let painting = false;
    let brushSize = 5;
    let brushPos = {x: 0, y: 0};


    function getBrushPos(canvasCtx, e) {
        let x = e.type.includes("touch") ?
            e.touches[0].clientX : e.clientX;
        let y = e.type.includes("touch") ?
            e.touches[0].clientY : e.clientY;
        let rect = canvasCtx.getBoundingClientRect();
        return {
            x: x - rect.left,
            y: y - rect.top
        };
    }

    //drawing
    function start(e) {
        painting = true;
        ctx.beginPath();
        brushPos = getBrushPos(canvas, e);
        ctx.moveTo(brushPos.x, brushPos.y);
        draw(e);
        e.preventDefault();
    }

    function draw(e) {
        if (!painting) return;
        ctx.lineWidth = brushSize;
        ctx.lineCap = 'round';
        brushPos = getBrushPos(canvas, e);
        ctx.lineTo(brushPos.x, brushPos.y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(brushPos.x, brushPos.y);
        e.preventDefault();
    }

    function end(e) {
        ctx.closePath();
        painting = false;
        e.preventDefault();
    }

    canvas.addEventListener('mousedown', start);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', end);
    canvas.addEventListener('mouseout', end);
    canvas.addEventListener('touchstart', start);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', draw);


    document.addEventListener('click', (e) => {
        let x = e.target
        if (x.id === 'reset') ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

});
// function guess_category (){
//
//     let guess_name;
//     if (!isCanvasBlank(canvas)) {
//         let image = canvas.toDataURL("image/png");
//
//         guess_name = $.post(guess_link, {
//             // category: category_name,
//             save_image: image,
//         });
//         document.getElementById('guess_id').innerHTML = guess_name.name;
//     }
//
// }
function guess_category() {
    if (!isCanvasBlank(canvas)){
        let image = canvas.toDataURL("image/png")
        $.post(guess_link, {picture: image}, function myCallback(data) {
        document.getElementById('guess_id').innerHTML = data.category;
    });
    }

}

function isCanvasBlank(canvas) {
  return !canvas.getContext('2d')
    .getImageData(0, 0, canvas.width, canvas.height).data
    .some(channel => channel !== 0);
}