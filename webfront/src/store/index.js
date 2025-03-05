import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    username: '',
    datetime: ''
  },
  getters: {
    getUsername: state => state.username,
    getDatetime: state => state.datetime
  },
  mutations: {
    SET_USERNAME(state, username) {
      state.username = username;
    },
    SET_DATETIME(state, datetime) {
      state.datetime = datetime;
    }
  },
  actions: {
    updateUser({ commit }, userData) {
      commit('SET_USERNAME', userData.username);
      commit('SET_DATETIME', userData.datetime);
    }
  },
  modules: {
  }
})
