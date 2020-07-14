<template>
  <b-container>
    <h2>Browse similarity</h2>
    <b-row flex align-h="around">
      <PytorchModelMenu v-model="pytorch_model_id" />
    </b-row>
    <b-card no-body v-if="!!seed_image" header="Similarity results">
      <div class="m-3">
        <h4>Seed image</h4>
        <PhotographListItem :photograph="seed_image" />
      </div>
      <b-overlay :show="!loaded">
        <div v-if="!!nearest_neighbors">
          <hr />
          <h4 class="ml-3">50 Nearest Neighbors</h4>
          <b-list-group>
            <b-list-group-item v-for="img in nearest_neighbors" :key="img.id">
              <PhotographListItem :photograph="img" />
            </b-list-group-item>
          </b-list-group>
        </div>
      </b-overlay>
    </b-card>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import PytorchModelMenu from "@/components/PytorchModelMenu.vue";
import PhotographListItem from "@/components/PhotographListItem.vue";
export default {
  name: "Similarity",
  components: {
    PytorchModelMenu,
    PhotographListItem
  },
  props: {
    seed_image_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      pytorch_model_id: null,
      n_neighbors: 50,
      loaded: false
    };
  },
  computed: {
    state_ids() {
      var ids = {};
      if (!!this.pytorch_model_id) {
        ids["pytorch_model_id"] = this.pytorch_model_id;
      }
      ids["n_neighbors"] = this.n_neighbors;
      return ids;
    }
  },
  asyncComputed: {
    seed_image() {
      if (!!this.seed_image_id) {
        return HTTP.get("/photograph/" + this.seed_image_id + "/").then(
          results => {
            return results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    nearest_neighbors() {
      this.loaded = false;
      if (!!this.pytorch_model_id & !!this.seed_image_id) {
        return HTTP.post(
          "/pytorch_model/" + this.pytorch_model_id + "/get_nn/",
          {
            photograph: this.seed_image_id,
            n_neighbors: this.n_neighbors
          }
        ).then(
          results => {
            this.loaded = true;
            return results.data.slice(1);
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    }
  },
  methods: {
    format_distance(distance) {
      return distance.toFixed(5);
    },
    pic_variant(img) {
      if (!!img.job & !!this.seed_image.job) {
        if (img.job.id == this.seed_image.job.id) {
          return "primary";
        }
      } else {
        return null;
      }
    }
  },
  watch: {
    state_ids() {
      this.$router.push({ name: "Similarity", query: this.state_ids });
    }
  },
  mounted() {
    if (!!this.$route.query.n_neighbors) {
      this.n_neighbors = this.$route.query.n_neighbors;
    }
  }
};
</script>