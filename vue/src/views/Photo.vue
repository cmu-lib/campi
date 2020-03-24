<template>
  <div v-if="!!image_data">
    <p>
      <a :href="image_data.image.full">Full image</a>
    </p>
    <IIIF :info_url="image_data.image.info" />
  </div>
</template>

<script>
import IIIF from "@/components/IIIF";
import { HTTP } from "@/main";
export default {
  name: "Photo",
  components: {
    IIIF
  },
  props: {
    id: Number
  },
  data() {
    return {};
  },
  asyncComputed: {
    image_data() {
      return HTTP.get("/photograph/" + this.id + "/").then(
        results => {
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>
