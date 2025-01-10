<template>
    <div>
        <div class="section-card" v-if="profile" ref="headerSabaiCard">
            <div class="bg-web-banner card-1 img-cover">
                <div class="wrapper">
                </div>
            </div>
        </div>
        <div class="profile-card" v-if="profile">
            <div class="profile-header">
                <img :src="profile.pictureUrl" alt="User Picture" class="profile-pic">
                <h2 class="profile-name">{{ profile.displayName }}</h2>
            </div>
            <div class="profile-body">
                <div ref="memberLogin" v-if="member">
                    <div class="profile-item">
                        <span class="label">Status Message:</span>
                        <span>{{ profile.statusMessage || 'No status message' }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">First Name:</span>
                        <span>{{ memberData.firstname }}</span>
                    </div>
                        <div class="profile-item">
                        <span class="label">Last Name:</span>
                        <span>{{ memberData.lastname }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Email:</span>
                        <span>{{ memberData.email }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Date of Birth:</span>
                        <span>{{ memberData.dob }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Phone:</span>
                        <span>{{ memberData.phone }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Gender:</span>
                        <span>{{ memberData.gender }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Address:</span>
                        <span>{{ memberData.address }}</span>
                    </div>
                    <div class="profile-item">
                        <span class="label">Point Collection:</span>
                        <span>176 แต้ม</span>
                    </div>
                    
                </div>
                <div class="formbold-main-wrapper" ref="registerForm">
                    <div class="formbold-form-wrapper">
                        <div class="formbold-steps">
                            <ul>
                                <li :class="{ active: currentStep === 1 }">
                                    <span>1</span>
                                </li>
                                <li :class="{ active: currentStep === 2 }">
                                    <span>2</span>
                                </li>
                                <li :class="{ active: currentStep === 3 }">
                                    <span>3</span>
                                </li>
                            </ul>
                        </div>
    
                        <form @submit.prevent="handleSubmit">
                            <!-- Step 1 -->
                            <div class="formbold-form-step-1" v-show="currentStep == 1">
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="firstname" class="formbold-form-label">First name</label>
                                        <input v-model="formData.firstname" type="text" required placeholder="ใจดี" id="firstname" class="formbold-form-input" />
                                    </div>
                                </div>
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="lastname" class="formbold-form-label">Last name</label>
                                        <input v-model="formData.lastname" type="text" required placeholder="ช้อบสบาย" id="lastname" class="formbold-form-input" />
                                    </div>
                                </div>
    
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="dob" class="formbold-form-label">Date of Birth</label>
                                        <input v-model="formData.dob" type="date" required id="dob" class="formbold-form-input" />
                                    </div>
                                </div>
                                <div class="formbold-input-flex">
                                    <label for="gender" class="formbold-form-label">Gender</label>
                                    <select v-model="formData.gender" required id="gender" class="formbold-form-input">
                                        <option value="" disabled selected>Select Gender</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                    </select>
                                </div>
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="email" class="formbold-form-label">Email</label>
                                        <input v-model="formData.email" type="email" required placeholder="example@mail.com" id="email" class="formbold-form-input" />
                                    </div>
                                </div>
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="phone" class="formbold-form-label">Phone Number</label>
                                        <input v-model="formData.phone" type="tel" id="phone" placeholder="Enter your phone number" class="formbold-form-input" @input="formatPhoneNumber" />
                                        <p v-if="phoneError" class="error-message">{{ phoneError }}</p>
                                    </div>
                                </div>
    
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="address" class="formbold-form-label">Address</label>
                                        <input v-model="formData.address" type="text" id="address" required placeholder="Flat 4, 24 Castle Street, Perth" class="formbold-form-input" />
                                    </div>
                                </div>
                            </div>
    
                            <!-- Step 2 -->
                            <div class="formbold-form-step-2" v-show="currentStep == 2">
                                <div>
                                    <p><b>รายละเอียดและเงื่อนไข </b></p><br/>
                                    <p>
                                        <ul>
                                            <li>รับแต้มสะสม 1 แต้ม เมื่อซื้อสินค้าครบทุก 25 บาท ที่ซีเจ มอร์ และแบรนด์ในเครือทุกสาขาทั่วประเทศ (ยกเว้นเครื่องดื่มแอลกอฮอล์ทุกประเภท บุหรี่ บัตรเติมเงิน การเติมเงินผ่านเครื่อง U Top-Up สินค้าบริการ สินค้านมผงดัดแปลงสำหรับทารก
                                                และนมดัดแปลงสูตรต่อเนื่องสำหรับทารกและเด็ก สูตร 1 และสูตร 2 สินค้าหน่วยลัง และสินค้าหน่วยกระสอบ)</li>
    
                                            <li>แสดงบัตรสมาชิก หมายเลขสมาชิก หรือแจ้งหมายเลขโทรศัพท์ หรือหมายเลขประจำตัวประชาชนที่ผูกกับบัตรฯ แก่พนักงานทุกครั้งก่อนชำระเงิน เพื่อรับสิทธิประโยชน์</li>
    
                                            <li>แต้มสะสมในปีพ.ศ. ปัจจุบัน มีอายุการใช้งานถึงวันสุดท้าย (วันที่ 31 ธันวาคม) ของปีพ.ศ. ถัดไป เช่น แต้มที่สะสมในปี พ.ศ. 2567 จะหมดอายุในวันที่ 31 ธันวาคม 2568</li>
    
                                            <li>แต้มสะสมไม่สามารถแลก หรือทอนเป็นเงินสด</li>
    
                                            <li>บริษัทฯ ขอสงวนสิทธิ์การสมัครบัตรสมาชิกสบายการ์ด โดย 1 หมายเลขประจำตัวประชาชน ต่อ 1 หมายเลขสมาชิกเท่านั้น และบริษัทฯ ขอสงวนสิทธิ์การยกเลิกสิทธิประโยชน์ของสมาชิกใบเดิม กรณีพบว่าสมาชิก 1 ท่าน มีหมายเลขสมาชิกมากกว่า
                                                1 หมายเลข</li>
    
                                            <li>บริษัทฯ ขอสงวนสิทธิ์การเปลี่ยนแปลงเงื่อนไขของระบบสมาชิก โดยจะแจ้งให้ทราบล่วงหน้า</li>
    
                                        </ul>
                                    </p>
                                </div>
                            </div>
    
                            <!-- Step 3 -->
                            <div class="formbold-form-step-3" v-show="currentStep == 3">
                                <div class="formbold-form-confirm">
                                    <p>Please confirm the details below:</p>
                                    <pre>{{ formData }}</pre>
                                </div>
                            </div>
    
                            <!-- Buttons -->
                            <div class="formbold-form-btn-wrapper">
                                <button type="button" v-if="currentStep > 1" class="formbold-back-btn active" @click="prevStep">
                                                                        Back
                                                                        </button>
                                <button type="submit" class="formbold-btn">{{ currentStep === 3 ? 'Submit' : 'Next Step' }}</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

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
            profile: null,
            member: null,
            friendShip: null,
            email: null,
            os: null,
            appLanguage: null,
            liffLanguage: null,
            liffVersion: null,
            lineVersion: null,
            isInClient: null,
            isApiAvailable: null,
            isShowButton: false,
            message: "",
            error: "",
            currentStep: 1,
            formData: {
                firstname: '',
                lastname: '',
                dob: '',
                email: '',
                address: '',
                phone: '',
                gender: '',
            },
            memberData: {
                firstname: '',
                lastname: '',
                dob: '',
                email: '',
                address: '',
                phone: '',
                gender: '',
            },
        
            phoneError: '',
        };
    },
    async mounted() {
        await this.checkLiffLogin()
    },
    methods: {
        async checkLiffLogin() {
            await liff.ready.then(async () => {
                if (!liff.isLoggedIn()) {
                    liff.login({ redirectUri: window.location })
                } else {

                    const profile = await liff.getProfile();
                    this.profile = profile;

                    await this.checkIsExistingUser(this.profile.userId)

                    const friendShip = await liff.getFriendship()
                    this.friendShip = friendShip.friendFlag
                    // console.log(friendShip);
                    // ดึงข้อมูลอีเมล
                    const deIdToken = liff.getDecodedIDToken();
                    console.log(deIdToken);
                    this.email = deIdToken.email;

                    const idToken = liff.getIDToken();
                    console.log(idToken);

                    // ดึงข้อมูลต่าง ๆ ของ LIFF
                    this.os = liff.getOS();
                    this.appLanguage = liff.getAppLanguage();
                    this.liffLanguage = liff.getLanguage();
                    this.liffVersion = liff.getVersion();
                    this.lineVersion = liff.getLineVersion();
                    this.isInClient = liff.isInClient();
                    if (liff.isInClient()) {
                        this.isShowButton = true
                    }
                    this.isApiAvailable = liff.isApiAvailable('shareTargetPicker'); // ตัวอย่างการตรวจสอบ API

                }
            })
        },
        nextStep() {
            if (this.currentStep < 3) this.currentStep++;
        },
        prevStep() {
            if (this.currentStep > 1) this.currentStep--;
        },
        handleSubmit() {
            if (this.currentStep < 3) {
                this.nextStep();
            } else {
                console.log(this.formData);
                this.addNewUser();
                alert('Form Submitted Successfully!');
                const form = this.$refs.registerForm;
                if (form) {
                    form.style.display = 'none';
                }
            }
        },
        formatPhoneNumber(event) {
            const input = event.target.value.replace(/\D/g, ''); // เอาตัวเลขเท่านั้น
            let formattedNumber = '';

            if (input.length > 0) {
                formattedNumber += input.slice(0, 3);
            }
            if (input.length >= 4) {
                formattedNumber += '-' + input.slice(3, 6);
            }
            if (input.length >= 7) {
                formattedNumber += '-' + input.slice(6, 10);
            }

            this.formData.phone = formattedNumber;

            // ตรวจสอบความยาวเบอร์โทร
            if (input.length > 10) {
                this.phoneError = 'Phone number should not exceed 10 digits.';
            } else {
                this.phoneError = '';
            }
        },
        async addNewUser() {
            const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_gcf_data_store_manager'
            const payload = {
                action: "insert",
                kind: "CJ_USER",
                "id": this.profile.userId,
                data: this.formData
            };
            const response = await axios.post(gcf_url, payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        },
        async checkIsExistingUser(userId) {
            const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_gcf_data_store_manager'
            const payload = {
                action: "get",
                kind: "CJ_USER",
                "id": userId,
            };
            const response = await axios.post(gcf_url, payload, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.status == 200) {
                const form = this.$refs.registerForm;
                if (form) {
                    form.style.display = 'none';
                    this.member = true;
                    this.memberData.phone =  response.data.phone
                    this.memberData.address =  response.data.address
                    this.memberData.dob =  response.data.dob
                    this.memberData.email =  response.data.email
                    this.memberData.firstname =  response.data.firstname
                    this.memberData.lastname =  response.data.lastname
                }
            }
        },

    },
};
</script>

<style scoped>
@import './assets/styles/main.css';
@import './assets/styles/register.css';
</style>