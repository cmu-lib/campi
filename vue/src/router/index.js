import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from "@/views/Home.vue"
import Browse from '@/views/Browse.vue'
import Photo from "@/views/Photo.vue"
import Similarity from "@/views/Similarity.vue"

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
    path: "/similiarity",
    name: "Similarity",
    component: Similarity,
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
