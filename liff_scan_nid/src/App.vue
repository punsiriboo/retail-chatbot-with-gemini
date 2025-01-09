
<template>
    <div class="web-camera-container">
        <div class="camera-button">
            <button type="button" class="button is-rounded" :class="{ 'is-primary' : !isCameraOpen, 'is-danger' : isCameraOpen}" @click="toggleCamera">
            								            <span v-if="!isCameraOpen">Open Camera</span>
            								            <span v-else>Close Camera</span>
            								        </button>
        </div>
    
        <div v-show="isCameraOpen && isLoading" class="camera-loading">
            <ul class="loader-circle">
                <li></li>
                <li></li>
                <li></li>
            </ul>
        </div>
    
        <div v-if="isCameraOpen" v-show="!isLoading" class="camera-box" :class="{ 'flash' : isShotPhoto }">
    
            <div class="camera-shutter" :class="{'flash' : isShotPhoto}"></div>
    
            <video v-show="!isPhotoTaken" ref="camera" :width="450" :height="337.5" autoplay muted playsinline></video>
    
            <canvas v-show="isPhotoTaken" id="photoTaken" ref="canvas" :width="450" :height="337.5"></canvas>
        </div>
    
        <div v-if="isCameraOpen && !isLoading" class="camera-shoot">
            <button type="button" class="button" @click="takePhoto">
            								        <img src="https://img.icons8.com/material-outlined/50/000000/camera--v2.png">
            								    </button>
        </div>
    
        <div v-if="isPhotoTaken && isCameraOpen" class="camera-download">
            <a id="downloadPhoto" download="my-photo.jpg" class="button" role="button" @click="downloadImage">
            								        Download
            								    </a>
        </div>
    </div>
</template>

<style scoped>
body {
    display: flex;
    justify-content: center;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
    font-family: Arial, sans-serif;
    height: 100vh;
    overflow: hidden;
    /* Prevent scrolling */
}

.web-camera-container {
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100vh;
    /* Full viewport height */
    box-sizing: border-box;
    background-color: #000;
    /* Black background for better camera contrast */
    overflow: hidden;
}

.camera-box {
    position: relative;
    width: 100%;
    /* Full width */
    height: calc(100vh - 150px);
    /* Subtracting space for buttons */
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #000;
    overflow: hidden;
    /* Prevent overscrolling on iOS */
}

.camera-box video,
.camera-box canvas {
    width: 100%;
    /* Full width */
    height: auto;
    /* Maintain aspect ratio */
    object-fit: cover;
    /* Ensures the video fills the area without distortion */
    max-height: calc(100vh - 150px);
    /* Prevent video overflow */
}

.camera-button {
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
    width: 100%;
}

.camera-shoot,
.camera-download {
    margin: 1rem 0;
    display: flex;
    justify-content: center;
    width: 100%;
}

.camera-shoot button {
    height: 60px;
    width: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: #fff;
    border: none;
    cursor: pointer;
}

.camera-shoot button img {
    height: 35px;
    object-fit: cover;
}

.camera-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
}
</style>

<script>
export default {
    data() {
        return {
            isCameraOpen: false,
            isPhotoTaken: false,
            isShotPhoto: false,
            isLoading: false,
            link: "#",
        };
    },

    methods: {
        toggleCamera() {
            if (this.isCameraOpen) {
                this.closeCamera();
            } else {
                this.openCamera();
            }
        },

        openCamera() {
            this.isCameraOpen = true;
            this.isLoading = true;

            const constraints = {
                audio: false,
                video: {
                    facingMode: "environment", // Use back camera
                },
            };

            navigator.mediaDevices
                .getUserMedia(constraints)
                .then((stream) => {
                    this.isLoading = false;
                    this.$refs.camera.srcObject = stream;
                })
                .catch((error) => {
                    this.isLoading = false;
                    alert(
                        "Camera access failed. Please check your browser's permissions or try a different browser."
                    );
                });
        },

        closeCamera() {
            if (this.$refs.camera && this.$refs.camera.srcObject) {
                const tracks = this.$refs.camera.srcObject.getTracks();
                tracks.forEach((track) => track.stop());
            }
            this.isCameraOpen = false;
            this.isPhotoTaken = false;
            this.isShotPhoto = false;
        },

        takePhoto() {
            if (!this.isCameraOpen || this.isLoading) {
                alert("Camera is not open or still loading.");
                return;
            }

            const context = this.$refs.canvas.getContext("2d");
            context.drawImage(this.$refs.camera, 0, 0, 450, 337.5);

            this.isPhotoTaken = true;
            this.triggerFlashEffect();
        },

        triggerFlashEffect() {
            this.isShotPhoto = true;
            const FLASH_TIMEOUT = 50;

            setTimeout(() => {
                this.isShotPhoto = false;
            }, FLASH_TIMEOUT);
        },

        downloadImage() {
            if (!this.isPhotoTaken) {
                alert("No photo taken to download.");
                return;
            }

            const canvas = this.$refs.canvas;
            const downloadLink = this.$refs.downloadPhoto;
            const imageDataUrl = canvas
                .toDataURL("image/jpeg")
                .replace("image/jpeg", "image/octet-stream");

            downloadLink.setAttribute("href", imageDataUrl);
            downloadLink.setAttribute("download", "photo.jpg");
        },
    },
};
</script>
