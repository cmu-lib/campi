<template>
  <b-container fluid>
    <h2>Browse similarity</h2>
    <b-row>
      <b-col cols="3">
        <PytorchModelMenu v-model="pytorch_model" />
        <AnnoyIdxMenu v-if="!!pytorch_model" v-model="annoy_idx" :pytorch_model="pytorch_model" />
      </b-col>
      <b-col cols="9"></b-col>
    </b-row>
  </b-container>
</template>

<script>
import PytorchModelMenu from "@/components/PytorchModelMenu.vue";
import AnnoyIdxMenu from "@/components/AnnoyIdxMenu.vue";
export default {
  name: "Similarity",
  components: {
    PytorchModelMenu,
    AnnoyIdxMenu
  },
  data() {
    return {
      pytorch_model: null,
      annoy_idx: null,
      seed_image_id: null
    };
  },
  asyncComputed: {}
};
</script>