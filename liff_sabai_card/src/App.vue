<template>
    <div>
        <div class="section-card" ref="headerSabaiCard">
            <div class="bg-web-banner card-1 img-cover">
                <div class="wrapper">
                </div>
            </div>
        </div>
        <div v-if="isLoading" class="centered">
            <div class="camera-loading loader"></div>
        </div>
        <div class="profile-card" v-if="profile">
            <div class="profile-header">
                <img :src="this.profile.picture" alt="User Picture" class="profile-pic">
                <h2 class="profile-name">{{ this.profile.name }}</h2>
            </div>
            <div class="profile-body">
                <div ref="memberLogin" v-if="member">
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
                        <span>{{ memberData.point }}</span>
                    </div>
    
                </div>
                <div v-if="isFormRegister" class="formbold-main-wrapper" ref="registerForm">
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
                                        <label for="nid" class="formbold-form-label">National ID</label>
                                        <input v-model="formData.nid" type="number" required placeholder="1000000000000" id="nid" class="formbold-form-input" @input="formatNID" />
                                        <p v-if="nidError" class="error-message">{{ nidError }}</p>
                                    </div>
                                </div>
    
                                <div class="formbold-input-flex">
                                    <div>
                                        <label for="dob" class="formbold-form-label">Date of Birth</label>
                                        <input v-model="formData.dob" type="date" required id="dob" class="formbold-form-input" />
                                    </div>
                                </div>
                                <div class="formbold-input-flex">
                                    <div class="formbold-input-radio-wrapper">
                                        <label for="gender" class="formbold-form-label">Select Gender</label>
                                        <div class="formbold-radio-flex">
                                            <div class="formbold-radio-group">
                                                <label class="formbold-radio-label">
                                                        <input 
                                                            v-model="formData.gender" 
                                                            class="formbold-input-radio" 
                                                            type="radio" 
                                                            name="gender" 
                                                            id="gender-male" 
                                                            value="Male"
                                                        >
                                                        Male
                                                        <span class="formbold-radio-checkmark"></span>
                                                    </label>
                                            </div>
    
                                            <div class="formbold-radio-group">
                                                <label class="formbold-radio-label">
                                                        <input 
                                                            v-model="formData.gender" 
                                                            class="formbold-input-radio" 
                                                            type="radio" 
                                                            name="gender" 
                                                            id="gender-female" 
                                                            value="Female"
                                                        >
                                                        Female
                                                        <span class="formbold-radio-checkmark"></span>
                                                    </label>
                                            </div>
                                        </div>
                                    </div>
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
                <div v-if="isDoneRegistration" class="formbold-main-wrapper flex-wrap">
                    <img style="width: 100%; max-width: 100%; height: auto;" src="https://storage.googleapis.com/line-cj-demo-chatboot/web/recommmend_friend.png" alt="Invite Friends" class="invite-friends"></img> 
                    <h4> คุณสมัครสมาชิก CJ สำเร็จแล้ว คุณสามารถใช้บัตรสมาชิก CJ ได้ทันที </h4>
                    <p> คุณสามารถแนะนำเพื่อนๆของคุณมาสมัครสมาชิกบัตรสบายการ์ดได้เพื่อรับแต้มสะสมพิเศษเพิ่มเติมในการแลกซื้อสินค้าจากเรา</p>
                       
                    <!-- Buttons -->
                    <div class="formbold-form-btn-wrapper btn-flex">
                        <button type="button" class="formbold-btn" @click="backToChat">Back to Chat</button>
                        <button type="button" class="formbold-btn" @click="recomendFriend">Recommend Friend</button>
                        <button type="button" class="formbold-btn" @click="myProfile">My Profile</button>
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
            isLoading: false,
            isFormRegister: false,
            isDoneRegistration: true,
            profile: {
                name: null,
                picture: null,
                userId: null,
                idToken: null,
            },
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
                nid: '',
                dob: '',
                email: '',
                address: '',
                phone: '',
                gender: 'Female',
            },
            memberData: {
                firstname: '',
                lastname: '',
                nid: '',
                dob: '',
                email: '',
                address: '',
                phone: '',
                gender: '',
            },
            phoneError: '',
            nidError: '',
        };
    },
    async mounted() {
        this.isLoading = true;
        await this.checkLiffLogin()
    },
    methods: {     
        backToChat() {
            liff.permission.requestAll();
            liff.sendMessages([{
                type: 'text',
                text: 'CJ_MEMBER:สมัครสมาชิก CJ สำเร็จแล้วค่ะ'
            }]).then(() => {
                liff.closeWindow();
            }).catch((err) => {
                console.error(err);
            });
        },
        preFilledDataFromParams() {
            const queryString = window.location.search;
            console.log(queryString);

            const urlParams = new URLSearchParams(queryString);
            const firstname = urlParams.get('first_name_th');
            const lastname = urlParams.get('last_name_th');
            const nid = urlParams.get('nid');
            const dob = urlParams.get('dob');
            const address = urlParams.get('address');
            const gender = urlParams.get('gender');
            console.log(firstname, lastname, nid, dob, address, gender);

            if (firstname) {
                this.formData.firstname = firstname;
            }
            if (lastname) {
                this.formData.lastname = lastname;
            }
            if (nid) {
                this.formData.nid = nid;
            }
            if (dob) {
                this.formData.dob = dob;
            }
            if (address) {
                this.formData.address = address;
            }
            if (gender) {
                this.formData.gender = gender;
            }
        },
        myProfile() {
            this.isFormRegister = false;
            this.isDoneRegistration = false;
            this.checkIsExistingUser(this.profile.userId);
        },
        recomendFriend() {
            console.log(this.profile);
            const inivitationText = "คุณได้รับคำเชิญจากคุณ " + this.profile.name + " ให้มาสมัครเป็นสมาชิกบัตรสบายการ์ด"
            const textMessage = {
                type: 'text',
                text: inivitationText
            };
            const flexBubble = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://storage.googleapis.com/line-cj-demo-chatboot/web/sabaicard-invite.png",
                    "size": "full",
                    "aspectRatio": "23:20",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [{
                            "type": "text",
                            "text": "สมัครเป็นสมาชิกบัตรสบายการ์ด สิทธิพิเศษ และส่วนลดที่มากกว่า",
                            "wrap": true,
                            "weight": "bold",
                            "gravity": "center",
                            "size": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [{
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [{
                                        "type": "image",
                                        "url": this.profile.picture,
                                        "aspectMode": "cover",
                                        "size": "full"
                                    }],
                                    "cornerRadius": "100px",
                                    "width": "72px",
                                    "height": "72px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [{
                                        "type": "text",
                                        "text": inivitationText,
                                        "weight": "bold",
                                        "color": "#000000",
                                        "size": "sm",
                                        "wrap": true
                                    }]
                                }
                            ],
                            "spacing": "xl",
                            "paddingAll": "20px"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "สมัครสมาชิกเลย",
                                "uri": "https://liff.line.me/2006689746-nGpDmd7r?recommomend_by=" + this.profile.userId
                            },
                            "style": "primary",
                            "color": "#00A150"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "ดูรายละเอียดเพิ่มเติม",
                                "uri": "https://www.cjexpress.co.th/member/"
                            },
                            "style": "secondary"
                        }
                    ],
                    "spacing": "sm"
                }
            }
            const flexMessage = {
                type: 'flex',
                altText: 'ชวนมาเป็นสมาชิกบัตรสบายการ์ด',
                contents: flexBubble
            };
            console.log(flexMessage);
            console.log(textMessage);
            liff.permission.requestAll();
            liff.shareTargetPicker([
                textMessage,
                flexMessage
            ])
            .then(() => {
                console.log("Share target picker was launched");
                liff.closeWindow();
            })
            .catch((err) => {
                console.error(err);
            });
        },
        async checkLiffLogin() {
            await liff.ready.then(async () => {
                if (!liff.isLoggedIn()) {
                    liff.login({ redirectUri: window.location })
                } else {
                    console.log('Get data from URL params');
                    this.preFilledDataFromParams();

                    const deIdToken = liff.getDecodedIDToken();
                    console.log(deIdToken);
                    this.profile.name = deIdToken.name;
                    this.profile.picture = deIdToken.picture;
                    this.profile.userId = deIdToken.sub;
                    const idToken = liff.getIDToken();
                    this.profile.idToken = idToken;

                    console.log(this.profile);

                    await this.checkIsExistingUser(this.profile.userId)

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
                    console.log(this.os);
                    console.log(this.appLanguage);
                    console.log(this.liffLanguage); 
                    console.log(this.liffVersion);
                    console.log(this.lineVersion);
                    console.log(this.isInClient);
                    console.log(this.isApiAvailable);
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
                this.isFormRegister = false;
                this.isDoneRegistration = true;
            }
        },
        formatNID(event) {
            const input = event.target.value.replace(/\D/g, ''); // เอาตัวเลขเท่านั้น
            if (input.length > 13) {
                this.nidError = 'National ID should not exceed 13 digits.';
            } else {
                this.nidError = '';
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
                id: this.profile.userId,
                data: {
                    ...this.formData, 
                    point: 0         
                }
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

            try {
                const response = await axios.post(gcf_url, payload, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (response.status == 200) {
                    this.isFormRegister = false;
                    this.member = true;
                    this.memberData.phone = response.data.phone
                    this.memberData.address = response.data.address
                    this.memberData.dob = response.data.dob
                    this.memberData.email = response.data.email
                    this.memberData.firstname = response.data.firstname
                    this.memberData.lastname = response.data.lastname
                    this.memberData.gender = response.data.gender
                    this.memberData.point = response.data.point
                    this.isLoading = false;
                }
            } catch (err) {
                if (err.response.status == 404) {
                    this.isLoading = false;
                    this.member = false;
                    this.isFormRegister = true;
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