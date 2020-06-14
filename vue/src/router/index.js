import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from "@/views/Home.vue"
import Browse from '@/views/Browse.vue'
import Photo from "@/views/Photo.vue"
import Similarity from "@/views/Similarity.vue"
import CloseMatch from "@/views/CloseMatch.vue"
import CloseMatchRunList from "@/views/CloseMatchRunList.vue"
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: "/browse",
    name: "Browse",
    component: Browse,
  },
  {
    path: "/browse/photograph/:id",
    name: "Photo",
    component: Photo,
    props: (route) => {
      return { id: Number(route.params.id) }
    }
  },
  {
    path: "/similiarity/photograph/:id",
    name: "Similarity",
    component: Similarity,
    props: (route) => {
      return { seed_image_id: Number(route.params.id) }
    },
  },
  {
    path: "/close_match",
    name: "CloseMatch",
    component: CloseMatch,

  },
  {
    name: "CloseMatchRunList",
    path: "/close_match/run/:id",
    component: CloseMatchRunList,
    props: (route) => {
      return { close_match_run_id: Number(route.params.id) }
    }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
