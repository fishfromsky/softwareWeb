<template>
    <div class="main">
        <div class="text-box">
            {{ headerName }}
        </div>
    </div>
</template>

<script>
export default {
    name: 'navheader',
    components: {

    },
    props: {
        headerName: {
            type: String,
            required: true
        }
    },
    data(){
        return {
            
        }
    }
}
</script>

<style scoped>
.main{
    width: 100%;
    height: 8vh;
    background-color: #40c9c6;;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
}
.text-box{
    font-size: 3vh;
    font-weight: bolder;
    color: #fff;
    margin-left: 20px;
}
</style>