
<template>
    <div>
        <div class="section-card" v-if="isbeforeCamera" ref="headerSabaiCard">
            <div class="bg-web-banner img-cover">
                <div class="wrapper">
                </div>
            </div>
        </div>
        <div class="section-card" v-if="isCheckUser || isLoading" ref="headerSabaiCard">
            <div class="bg-web-banner-2 img-cover">
                <div class="wrapper">
                </div>
            </div>
        </div>
        <div v-if="isCheckUser || isLoading" class="centered">
            <div class="camera-loading loader"></div>
        </div>
        <div class="web-camera-container" v-if="isbeforeCamera">
            <div><h4>กรุณาเตรียมบัตรประชาชนของท่านเพื่อถ่ายรูป สแกนบัตรประชาชน</h4></br></div>
            <div><img src="https://storage.googleapis.com/line-cj-demo-chatboot/web/Animation%20-%201736414808469.gif" alt="NID" style="width: 200px; height: auto;"></div>
            <div class="centered">
                <button v-if="!isCameraOpen" class="formbold-btn" @click="openCamera">
                    เริ่มสแกนบัตรประชาชน
                </button>
            </div>
        </div>
        <div v-if="isCameraOpen" class="web-camera-container">
            <div class="camera-box" :class="{ 'flash' : isShotPhoto }">
                <div class="camera-shutter" :class="{'flash' : isShotPhoto}"></div>
                <video v-show="!isPhotoTaken" ref="camera" autoplay muted playsinline></video>
                <canvas v-show="isPhotoTaken" id="photoTaken" ref="canvas"></canvas>
                <div class="nid-overlay-container">
                    <div class="nid-overlay">
                        <span class="overlay-text" ref="overlayText">กรุณาถ่ายรูปบัตรประชาชนของท่านภายในกรอบที่กำหนด</span>
                        <div class="nid-overlay-inner"></div>
                        <div v-show="isOCRDectecting" class="loader"></div>
                        <div v-show="isInvalidNID" class="warning-nid"></div>
                    </div>
                </div>
            </div>
    
            <div v-if="isCameraOpen && !isPhotoTaken" class="camera-shoot">
                <button type="button" class="button" @click="takePhoto">
                    <img src="https://img.icons8.com/material-outlined/50/000000/camera--v2.png">
                </button>
            </div>
    
            <div v-if="isPhotoTaken" class="camera-shoot">
                <button v-show="isInvalidNID" type="button" class="button" @click="retakePhoto">
                    <img src="https://storage.googleapis.com/line-cj-demo-chatboot/web/redo.png">
                </button>
                <button v-show="!isInvalidNID" type="button" class="button" @click="ocrImage" style="margin-left: 10px;">
                    <img src="https://storage.googleapis.com/line-cj-demo-chatboot/web/check.png">
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    display: flex;
    justify-content: center;
    margin: 0;
    padding: 0;
    font-family: "Inter", sans-serif;
    height: 100vh;
    overflow: hidden;
    /* Prevent scrolling */
}

.centered {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 10vh;
}

.web-camera-container {
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100vh;
    /* Full viewport height */
    box-sizing: border-box;
    overflow: hidden;
}

.camera-box {
    position: relative;
    width: 100%;
    height: 100%;
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
    height: 100%;
    position: absolute;
    object-fit: cover;
}

.camera-button {
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
    background-color: #eaeaea;
    border: none;
    cursor: pointer;
}

.camera-shoot button img {
    height: 35px;
    object-fit: cover;
}

.camera-loading {
    position: absolute;
    transform: translate(-50%, -50%);
    z-index: 9999;
}

.nid-overlay-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: none;
    /* Allow clicks to pass through to the video */
    z-index: 3;
    /* Ensure it overlays the video/canvas */
}

.nid-overlay {
    position: relative;
    border: 2px dashed #009e00;
    /* Dashed green border */
    border-radius: 8px;
    /* Rounded corners */
    width: 85%;
    /* Adjust for the expected size of the NID card */
    height: 85%;
    /* Typical aspect ratio of NID cards */
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.1);
    /* Optional semi-transparent background */
}

.overlay-text {
    position: absolute;
    top: -40px;
    /* Position above the box */
    font-size: 14px;
    color: #009e00;
    /* Green text color */
    background: rgb(255, 255, 255);
    /* Semi-transparent background */
    padding: 5px 10px;
    border-radius: 4px;
    text-align: center;
    white-space: nowrap;
    /* Prevent text from wrapping */
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3);
}

.nid-overlay .nid-overlay-inner {
    position: absolute;
    width: 95%;
    height: 90%;
    border: 1px solid rgba(255, 255, 255, 0.5);
    /* Inner guide border */
    border-radius: 4px;
}

.bg-web-banner {
    -webkit-text-size-adjust: 100%;
    --rem: 16;
    text-rendering: optimizeLegibility;
    font-size: 26px;
    line-height: 1.42857;
    box-sizing: border-box;
    background-repeat: no-repeat;
    background-image: url(https://storage.googleapis.com/line-cj-demo-chatboot/web/scan_nid_titile.png);
    width: 100%;
    background-position: center;
    background-size: cover;
    min-height: 200px;
    /* Set a reasonable minimum height */
    height: 35vh;
    /* Responsive height based on the viewport */
    max-height: 350px;
    /* Optional: Limit the max height for larger screens */
}

.bg-web-banner-2 {
    -webkit-text-size-adjust: 100%;
    --rem: 16;
    text-rendering: optimizeLegibility;
    font-size: 26px;
    line-height: 1.42857;
    box-sizing: border-box;
    background-repeat: no-repeat;
    padding: 0 40px;
    background-image: url(https://storage.googleapis.com/line-cj-demo-chatboot/web/sabai-card-center.png);
    width: 100%;
    background-position: center;
    background-size: cover;
    min-height: 200px; /* Set a reasonable minimum height */
    height: 35vh; /* Responsive height based on the viewport */
    max-height: 350px; /* Optional: Limit the max height for larger screens */
}

h4 {
    font-size: 1rem;
    font-weight: 500;
    color:  #009e00;
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 1rem;
    
}

.formbold-btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    margin: 0.5rem;
    border-radius: 0.25rem;
    background-color: #009e00;
    color: #fff;
    font-size: 1rem;
    font-weight: 500;
    text-align: center;
    cursor: pointer;
    border: none;
    transition: background-color 0.3s;
}

.formbold-btn:hover {
    box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.05);
}

.loader {
    width: 48px;
    height: 48px;
    border:10px solid #FFF;
    border-radius: 50%;
    position: relative;
    transform:rotate(45deg);
    box-sizing: border-box;
}
.loader::before {
    content: "";
    position: absolute;
    box-sizing: border-box;
    inset:-10px;
    border-radius: 50%;
    border:10px solid #009e00;
    animation: prixClipFix 2s infinite linear;
}

@keyframes prixClipFix {
    0%   {clip-path:polygon(50% 50%,0 0,0 0,0 0,0 0,0 0)}
    25%  {clip-path:polygon(50% 50%,0 0,100% 0,100% 0,100% 0,100% 0)}
    50%  {clip-path:polygon(50% 50%,0 0,100% 0,100% 100%,100% 100%,100% 100%)}
    75%  {clip-path:polygon(50% 50%,0 0,100% 0,100% 100%,0 100%,0 100%)}
    100% {clip-path:polygon(50% 50%,0 0,100% 0,100% 100%,0 100%,0 0)}
}

/* HTML: <div class="loader"></div> */
.warning-nid {
  width: fit-content;
  font-weight: bold;
  font-family: monospace;
  font-size: 30px;
  color: #0000;
  background: linear-gradient(90deg,#C02942 calc(50% + 0.5ch),#000 0) right/calc(200% + 1ch) 100%;
  -webkit-background-clip: text;
          background-clip: text;
  animation: l7 2s infinite steps(11);
}
.warning-nid:before {
  content:"Invalid National ID";
}
@keyframes l7 {to{background-position: left}}
      
</style>

<script>
import liff from "@line/liff";
import axios from "axios";

export default {
    beforeCreate() {
        liff
            .init({
                liffId: import.meta.env.VITE_LIFF_ID
            })
            .then(() => {
                this.message = "LIFF init succeeded.";
            })
            .catch((e) => {
                this.message = "LIFF init failed.";
                this.error = `${e}`;
            });
    },
    data() {
        return {
            isCheckUser: false,
            isbeforeCamera: false,
            isCameraOpen: false,
            isPhotoTaken: false,
            isShotPhoto: false,
            isLoading: false,
            isInvalidNID: false,
            isOCRDectecting: false,
            link: "#",
            idToken: null,
        };
    },
    async mounted() {
        this.isCheckUser = true;
        await this.checkLiffLogin()
        console.log(this.profile);
        if (this.profile) {
            this.checkIsExistingUser(this.profile.userId)
        }
    },
    methods: {
        async checkLiffLogin() {
            await liff.ready.then(async () => {
                if (!liff.isLoggedIn()) {
                    liff.login({ redirectUri: window.location })
                } else {

                    const profile = await liff.getProfile();
                    this.profile = profile;
                    console.log(profile);

                    const idToken = liff.getIDToken();
                    console.log(idToken);

                    const deIdToken = liff.getDecodedIDToken();
                    console.log(deIdToken);

                    this.os = liff.getOS();
                    this.appLanguage = liff.getAppLanguage();
                    this.liffLanguage = liff.getLanguage();
                    this.liffVersion = liff.getVersion();
                    this.lineVersion = liff.getLineVersion();
                    this.isInClient = liff.isInClient();
                    this.isApiAvailable = liff.isApiAvailable('shareTargetPicker'); // ตัวอย่างการตรวจสอบ API
                }
            })
        },
        retakePhoto() {
            this.isPhotoTaken = false;
            this.isOCRDectecting = false;
            this.isInvalidNID = false;
            this.$refs.overlayText.innerText = "กรุณาถ่ายรูปบัตรประชาชนของท่านภายในกรอบที่กำหนด";
        },
        openCamera() {
            this.isbeforeCamera = false;
            this.isCameraOpen = true;

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
            const videoWidth = this.$refs.camera.videoWidth;
            const videoHeight = this.$refs.camera.videoHeight;

            this.$refs.canvas.width = videoWidth;
            this.$refs.canvas.height = videoHeight;

            context.drawImage(this.$refs.camera, 0, 0, videoWidth, videoHeight);

            this.isPhotoTaken = true;
            this.triggerFlashEffect();
            this.$refs.overlayText.innerText = "⚠️ กรุณาตรวจสอบความชัดเจนของรูปภาพ ก่อนกดยืนยัน";
        },

        triggerFlashEffect() {
            this.isShotPhoto = true;
            const FLASH_TIMEOUT = 50;

            setTimeout(() => {
                this.isShotPhoto = false;
            }, FLASH_TIMEOUT);
        },
        async ocrImage() {
            const canvas = this.$refs.canvas; // Get the canvas element

            if (!canvas) {
                console.error("Canvas element not found!");
                return;
            }

            const imageDataURL = canvas.toDataURL('image/jpeg', 0.8); // Convert to data URL (JPEG with quality 0.8)
            const base64Image = imageDataURL.split(',')[1]; // Get the base64 image data
            console.log(base64Image);
            this.isOCRDectecting = true;
            const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_nid_ocr'
            const payload = {
                "image_base64": base64Image
            };
            const response = await axios.post(gcf_url, payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log(response.data);
            if(response.data.is_nid){

            }
            else {
                this.isInvalidNID = true;
                this.isLoading = false;
                this.isOCRDectecting = false;
                this.$refs.overlayText.innerText = "⚠️ กรุณาถ่ายรูปบัตรประชาชนใหม่อีกครั้ง";
            }
        },
        async checkIsExistingUser(userId) {
            const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_gcf_data_store_manager'
            const payload = {
                action: "get",
                kind: "CJ_USER",
                "id": userId,
            };

            try {
                const response = await axios.post(gcf_url, payload, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (response.status == 200) {
                    liff.login({ redirectUri: "https://liff.line.me/2006689746-AvlxaqLP" })
                }
            } catch (err) {
                if (err.response.status == 404) {
                    this.isCheckUser = false;
                    this.isbeforeCamera = true;
                }
            }
        },
    },
};
</script>
