
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
                <!-- <label>
                    <input
                        id="file"
                        name="file"
                        type="file"
                        accept="image/gif, image/jpeg, image/png"
                        style="display: none;"
                        @change="handleFileUpload"
                    >
                    <img
                        src="https://storage.googleapis.com/line-cj-demo-chatboot/web/image.png"
                    >
                </label> -->
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
@import './assets/main.css';
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
            profile: null,
            recommomend_by: null,
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
                    if (deIdToken.email) {
                        this.profile.email = deIdToken.email;
                    }

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
            this.$refs.overlayText.style.color = "black";
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
        handleFileUpload(event) {
            const context = this.$refs.canvas.getContext("2d");

            // Ensure video dimensions are set to the canvas
            const videoWidth = this.$refs.camera.videoWidth;
            const videoHeight = this.$refs.camera.videoHeight;
            this.$refs.canvas.width = videoWidth;
            this.$refs.canvas.height = videoHeight;

            const file = event.target.files[0];
            const validImageTypes = ['image/gif', 'image/jpeg', 'image/png'];

            if (file && validImageTypes.includes(file.type)) {
                const image = new Image();
                const reader = new FileReader();

                reader.onload = (e) => {
                    image.src = e.target.result;
                    image.onload = () => {
                        // Draw the uploaded image on the canvas
                        context.clearRect(0, 0, videoWidth, videoHeight); // Clear existing canvas content
                        context.drawImage(image, 0, 0, videoWidth, videoHeight);
                    };
                };
                reader.readAsDataURL(file);
            } else {
                console.error('Invalid file type or no camera feed available.');
            }
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
            this.$refs.overlayText.style.color = "black";
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
            this.$refs.overlayText.innerText = "กรุณารอสักครู่ กำลังตรวจสอบข้อมูลรูปภาพบัตรประชาชน...";
            this.$refs.overlayText.style.color = "black";
            const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_nid_ocr'
            const payload = {
                "image_base64": base64Image
            };
            const response = await axios.post(gcf_url, payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const response_data = response.data.data;
            if(response_data.is_nid){
                const redirectUrl = new URL("https://dataaibootcamp.web.app"); // Use URL constructor for easy parameter handling
                redirectUrl.searchParams.append("action", "register");
                redirectUrl.searchParams.append("nid", response_data.nid);
                redirectUrl.searchParams.append("first_name_th", response_data.first_name_th);
                redirectUrl.searchParams.append("last_name_th", response_data.last_name_th);
                redirectUrl.searchParams.append("dob", response_data.dob); 
                redirectUrl.searchParams.append("address", response_data.address);
                redirectUrl.searchParams.append("gender", response_data.gender);
                redirectUrl.searchParams.append("email", this.profile.email);
                redirectUrl.searchParams.append("refer_by", this.recommomend_by);
                window.location.href = redirectUrl.toString(); // Redirect to the URL with parameters
            }
            else {
                this.isLoading = false;
                this.isOCRDectecting = false;
                this.$refs.overlayText.innerText = "⚠️ รูปที่ตรวจสอบได้ไม่ใช่รูปบัตรประชาชน หรือมีความไม่ชัดเจน กรุณาถ่ายรูปบัตรประชาชนใหม่อีกครั้ง";
                this.$refs.overlayText.style.color = "red";
                this.isInvalidNID = true;
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
                    window.location.href = "https://dataaibootcamp.web.app";
                }
            } catch (err) {
                if (err.response.status == 404) {
                    this.isCheckUser = false;
                    this.isbeforeCamera = true;
                    const queryString = window.location.search;
                    const urlParams = new URLSearchParams(queryString);
                    this.recommomend_by = urlParams.get('recommomend_by');
                    console.log(this.recommomend_by);

                }
            }
        },
    },
};
</script>
