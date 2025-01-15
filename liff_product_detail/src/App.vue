<template>
  <div class="product-list">
      <h3>รายการสินค้าในตระกร้าของฉัน</h3>
      <div v-for="(item, index) in items" :key="index" class="product-item">
          <img :src="item.item_image_url" alt="Product Image" class="product-image" />
          <div class="product-details">
              <p><strong>{{ item.item_name }} (x{{ item.quantity }})</strong></p>
              <p>Price: ${{ item.item_price }}</p>
              <div>
                  <label>Quantity: </label>
                  <select v-model="item.quantity" @change="calculateTotal">
                      <option v-for="n in 10" :key="n" :value="n">{{ n }}</option>
                  </select>
              </div>
          </div>
          <button @click="removeItem(index)">Remove</button>
      </div>
      <div class="total-section">
          <h4>Total: ${{ calculateTotal() }}</h4>
      </div>
      <button @click="UpdateBasket" class="submit-btn">Update</button>
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
          // Aggregated data
          items: []
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
                  console.log(this.profile.userId);
                  this.rawItems = await this.getUserOrder(this.profile.userId);
                  this.aggregateItems();
              }
          })
      },
      async geminiGenerateProductExplain() {
        return await axios.get('https://asia-southeast1-dataaibootcamp.cloudfunctions.net/gemini_generate_product_explain')
      },
      async getUserOrder(userId) {
          const gcf_url = 'https://asia-southeast1-dataaibootcamp.cloudfunctions.net/cj_gcf_data_store_manager'
          const payload = {
              action: "get",
              kind: "cj_users_orders",
              "id": userId,
          };
          const response = await axios.post(gcf_url, payload, {
              headers: {
                  'Content-Type': 'application/json'
              }
          });
          if (response.status == 200) {
              return response.data['items']
          }
      },
      aggregateItems() {
          const aggregated = {};

          this.rawItems.forEach((item) => {
              const key = `${item.item_name}-${item.item_price}`;
              if (!aggregated[key]) {
                  aggregated[key] = { ...item, quantity: 1 };
              } else {
                  aggregated[key].quantity += 1;
              }
          });

          this.items = Object.values(aggregated);
      },
      // Remove item from the list
      removeItem(index) {
          this.items.splice(index, 1);
      },
      // Calculate total price dynamically
      calculateTotal() {
          return this.items
              .reduce(
                  (sum, item) => sum + parseFloat(item.item_price) * item.quantity,
                  0
              )
              .toFixed(2);
      },
      // Handle form submission
      UpdateBasket() {
          console.log("Submitted Items:", this.items);
          alert(`Order Submitted!\n${JSON.stringify(this.items, null, 2)}`);
          liff.closeWindow()
      }
  }
};
</script>

<style>
@import './assets/main.css';
</style>
