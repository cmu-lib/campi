<template>
  <div>
    <b-form-group
      id="model-help"
      description="Which computer vision model should be used to determine similarity?"
      label="Select embeddings model"
      label-for="model-input"
      required
    >
      <b-form-select
        id="model-help"
        v-if="!!pytorch_model_options"
        :value="pytorch_model_options[0].value"
        :options="pytorch_model_options"
        @input="$emit('input', $event)"
      />
    </b-form-group>
  </div>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "PytorchModelMenu",
  props: {
    value: null
  },
  computed: {
    pytorch_model_options() {
      if (!!this.pytorch_models) {
        return this.pytorch_models.map(x => {
          const text = x.label + " (" + x.n_dimensions + " dims)";
          return {
            value: x.id,
            text: text
          };
        });
      } else {
        return null;
      }
    }
  },
  asyncComputed: {
    pytorch_models() {
      return HTTP.get("/pytorch_model/").then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  watch: {
    pytorch_model_options() {
      this.$emit("input", this.pytorch_model_options[0].value);
    }
  }
};
</script>