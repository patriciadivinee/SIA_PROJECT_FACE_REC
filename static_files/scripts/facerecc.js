let videoStream;
let modalShown = false;
let isFrontCamera = true;

document.addEventListener('DOMContentLoaded', function () {
    var myModal = new bootstrap.Modal(document.getElementById('exampleModal'));

    myModal._element.addEventListener('shown.bs.modal', function () {
        modalShown = true;
        getFace();
    });

    myModal._element.addEventListener('hidden.bs.modal', function () {
        modalShown = false;
        stopCamera();
    });

    function openModal() {
        var emailInput = document.getElementById('emailaddress');
        if (emailInput.checkValidity()) {
            myModal.show();
        } else {
            emailInput.reportValidity();
        }
    }

    var emailButton = document.getElementById('show_face');
    if (emailButton) {
        emailButton.addEventListener('click', openModal);
    }
});

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getFace() {
const csrftoken = getCookie('csrftoken');

const video = document.getElementById('video-element')
const image = document.getElementById('img-element')
const emailaddress = document.getElementById('emailaddress').value;
video.width = 640; 
video.height = 480;

Promise.all([
    log = faceapi.nets.tinyFaceDetector.loadFromUri("/static_files/models/"),
  ]).then(startVideo)

function startVideo() {
if (navigator.mediaDevices.getUserMedia) {
    const facingMode = isFrontCamera ? 'user' : { exact: 'environment' };
    navigator.mediaDevices.getUserMedia({video: { facingMode: facingMode } })
    .then((stream) => {
        videoStream = stream
        video.srcObject = stream
        const {height, width} = stream.getTracks()[0].getSettings()

        video.style.transform = isFrontCamera ? 'scaleX(-1)' : 'scaleX(1)';

        video.addEventListener('play', () => {
            const canvas = faceapi.createCanvasFromMedia(video);
            const modal = document.getElementById('exampleModal');
            const vidDiv = modal.querySelector('.modal-body #vid-div');
            vidDiv.appendChild(canvas);
            
            const displaySize = { width: video.width, height: video.height }
            faceapi.matchDimensions(canvas, displaySize)

            let timer = 0;

            setInterval(async () => {
              const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
              const resizedDetections = faceapi.resizeResults(detections, displaySize)
              canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
              faceapi.draw.drawDetections(canvas, resizedDetections)

            console.log(detections.length)
            console.log(detections[0].score)

            if (detections.length == 1 && detections[0].score > 0.8) {
                timer++;
                if (timer >= 10) {
                    autoCapture();
                    timer = 0;
                }
            } else {
                timer = 0; 
            }
            }, 100)

        function autoCapture() {
            const track = videoStream.getVideoTracks()[0];
            const imageCapture = new ImageCapture(track);

            console.log(imageCapture);

            imageCapture.takePhoto().then((blob) => {
                console.log("took photo:", blob);
                const img = new Image(width, height);
                img.src = URL.createObjectURL(blob);
                img.style.transform = 'scaleX(-1)';
                img.setAttribute("name", "face-reco");
                image.append(img);

                video.classList.add('not-visible');

                canvas.classList.add('not-visible');
                const tracks = videoStream.getTracks();
                tracks.forEach(track => track.stop());
                video.srcObject = null;
                videoStream = null;

                const reader = new FileReader();

                reader.readAsDataURL(blob);
                reader.onloadend = () => {
                    const base64data = reader.result;
                    console.log(base64data);

                    const fd = new FormData();
                    fd.append('csrfmiddlewaretoken', csrftoken);
                    fd.append('face-reco', base64data);
                    fd.append('emailaddress', emailaddress);

                    $.ajax({
                        type: 'POST',
                        url: '/face/verified',
                        enctype: 'multipart/form-data',
                        data: fd,
                        processData: false,
                        contentType: false,
                        success: function (data) {
                            if (data.success) {
                                window.location.href = "/home";
                            } else {
                                window.location.href = "/face/login";
                                window.alert("Unauthorized login")
                            }
                        },
                        error: (err) => {
                            console.log(err);
                        },
                    });
                };
            }).catch((error) => {
                console.log('takePhoto() error: ', error);
            });
        }
    })
    .catch((error) => {
        console.log("Something went wrong!", error);
    });
})
}
}
}

function stopCamera() {
    const video = document.getElementById('video-element');
    const image = document.getElementById('img-element');
    const img = image.querySelector('img');
    const captureBtn = document.getElementById('capture-btn');
    
    if (video && videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        videoStream = null;
        image.removeChild(img);
        video.classList.remove('not-visible');
        captureBtn.classList.remove('not-visible');
    }
}