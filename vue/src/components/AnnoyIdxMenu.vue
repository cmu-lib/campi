<template>
  <div>
    <b-form-group
      id="idx-help"
      description="Which approximate nearest neighbor index should be used in the search?"
      label="Select index"
      label-for="idx-input"
    >
      <b-form-select
        id="idx-input"
        v-if="!!annoy_idx_options"
        :options="annoy_idx_options"
        @input="$emit('input', $event)"
        required="true"
      />
    </b-form-group>
  </div>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "PytorchModelMenu",
  props: {
    value: null,
    pytorch_model: {
      type: Object,
      required: true
    }
  },
  computed: {
    annoy_idx_options() {
      if (!!this.annoy_idxs) {
        return this.annoy_idxs.map(x => {
          const text = x.n_images + " images - " + x.n_trees + " trees";
          return {
            value: x.id,
            text: text,
            disabled: !x.index_built
          };
        });
      } else {
        return null;
      }
    }
  },
  asyncComputed: {
    annoy_idxs() {
      return HTTP.get("/annoy_idx/", {
        params: { pytorch_model: this.pytorch_model.id }
      }).then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>