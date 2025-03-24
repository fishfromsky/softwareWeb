import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    username: '',
    datetime: '',
    colors: []
  },
  getters: {
    getUsername: state => state.username,
    getDatetime: state => state.datetime,
    getColors: state => state.colors
  },
  mutations: {
    SET_USERNAME(state, username) {
      state.username = username;
    },
    SET_DATETIME(state, datetime) {
      state.datetime = datetime;
    },
    SET_COLORS(state, colors) {
      state.colors = colors;
    }
  },
  actions: {
    updateUser({ commit }, userData) {
      commit('SET_USERNAME', userData.username);
      commit('SET_DATETIME', userData.datetime);
      commit('SET_COLORS', userData.colors);
    }
  },
  modules: {
  }
})
