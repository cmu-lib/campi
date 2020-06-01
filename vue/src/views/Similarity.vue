<template>
  <b-container>
    <h2>Browse similarity</h2>
    <b-row flex align-h="around">
      <PytorchModelMenu v-model="pytorch_model" />
      <AnnoyIdxMenu v-model="annoy_idx" :pytorch_model="pytorch_model" />
      <b-form-group
        id="n_neighbor_help"
        :label="'Number of neighbors to find: ' + this.n_neighbors"
      >
        <b-form-input
          id="n_neighbor_input"
          v-model="n_neighbors"
          type="range"
          min="9"
          max="40"
          debounce="1000"
        />
      </b-form-group>
    </b-row>
    <b-row>
      <b-col cols="3">
        <b-card header="Jobs" no-body>
          <b-list-group flush v-if="!!jobs">
            <b-list-group-item v-for="job in jobs" :key="job.id">{{ job.label }}</b-list-group-item>
          </b-list-group>
        </b-card>
      </b-col>
      <b-col cols="9">
        <b-card no-body v-if="!!seed_image" header="Similarity results">
          <div class="m-3">
            <h4>Seed image</h4>
            <PhotographListItem :photograph="seed_image" />
          </div>
          <div v-if="!!nearest_neighbors">
            <hr />
            <h4 class="ml-3">Nearest Neighbors</h4>
            <b-list-group>
              <b-list-group-item
                v-for="img in nearest_neighbors"
                :key="img.id"
                :variant="pic_variant(img)"
              >
                <b-overlay v-if="!!nearest_neighbors" :show="!loaded">
                  <PhotographListItem :photograph="img" />
                </b-overlay>
              </b-list-group-item>
            </b-list-group>
          </div>
        </b-card>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import _ from "lodash";
import PytorchModelMenu from "@/components/PytorchModelMenu.vue";
import AnnoyIdxMenu from "@/components/AnnoyIdxMenu.vue";
import PhotographListItem from "@/components/PhotographListItem.vue";
export default {
  name: "Similarity",
  components: {
    PytorchModelMenu,
    AnnoyIdxMenu,
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
      pytorch_model: null,
      annoy_idx: null,
      n_neighbors: 10,
      loaded: false
    };
  },
  computed: {
    jobs() {
      if (!!this.nearest_neighbors) {
        var all_jobs = this.nearest_neighbors
          .map(x => {
            return x.job;
          })
          .filter(y => {
            return !!y;
          });
        return _.uniqBy(all_jobs, "id");
      } else {
        return null;
      }
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
      if (!!this.annoy_idx) {
        return HTTP.post("/annoy_idx/" + this.annoy_idx.id + "/get_nn/", {
          photograph: this.seed_image.id,
          n_neighbors: this.n_neighbors
        }).then(
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
  }
};
</script>