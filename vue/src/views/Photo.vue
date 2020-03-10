<template>
  <IIIF :info_url="info_url" />
</template>

<script>
import IIIF from "@/components/IIIF";
import { HTTP } from "@/main";
export default {
  name: "Photo",
  components: {
    IIIF
  },
  props: ["id"],
  data() {
    return {};
  },
  asyncComputed: {
    info_url() {
      return HTTP.get("/photograph/" + this.id + "/").then(
        results => {
          return results.data.image.info;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>
