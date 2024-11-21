<script setup>
  import { handleError, computed,ref } from 'vue'


  const resB= ref(null)
  const topic = ref('topic');
  const error = ref(null);
  const loading = ref(false);
  const isAnswered = ref(false);
  const qCount = ref(0);
  const correctAnswersCount = ref(0);
  const data= ref(null)
  async function fetchData(topic){
    loading.value= true;
    error.value=null;
    
    await fetch("http://127.0.0.1:8000/quiz/?topic="+topic)
    .then(response => response.json())
    .then(res => data.value =  JSON.parse(res))
    .catch(err => error.value = err)
    .finally(loading.value = false)
    
  }

  async function fetchDataFromPdf(){
    loading.value= true;
    error.value=null;
    
    await fetch("http://127.0.0.1:8000/quizFromPdf")
    .then(response => response.json())
    .then(res => data.value =  JSON.parse(res))
    .catch(err => error.value = err)
    .finally(loading.value = false)
    
  }

  function handleAnswerClick(is_correct){
    isAnswered.value = true;
    if (is_correct){
      correctAnswersCount.value++;
    }
  };

</script>

<template>
  <div id="app">
    <div class="main">
      <h1>QuizAI</h1>
      <input v-if="!data" v-model="topic" placeholder="Write a topic..." style="width: 400px; font-size: 1.3em;">
      <button v-if="!data" @click="fetchData(topic)">
        {{ loading ? "Loading": "Create Quiz" }}
      </button>

      <button v-if="!data" @click="fetchDataFromPdf()">
        {{ loading ? "Loading": "Create Quiz From Pdf" }}
      </button>

      <p v-if="data">Score: {{ correctAnswersCount}} / {{ data.length }}</p>
      <p v-if="error">{{ error }}</p>
      <div v-if="data" class="main_item">
        <h2>{{data[qCount].question}}</h2>
          <ul v-if="data[qCount].answers">
            <li v-for="(answer, index) in data[qCount].answers" :key="index">
              <button v-if="answer==data[qCount].correct_answer" @click="handleAnswerClick(answer == data[qCount].correct_answer)" :class="{correct : isAnswered}" :disabled="isAnswered">
                {{ answer }}
              </button>
              <button v-else @click="handleAnswerClick(answer == data[qCount].correct_answer)" :class="{incorrect : isAnswered}" :disabled="isAnswered">
                {{ answer }}
              </button>
            </li>
          </ul>
      </div>
      <button v-if="questionsLeft" @click="qCount++, isAnswered=false">
        Next Question
      </button>
      <button v-if="data" @click="data=null">
        Reset
      </button>
      

    </div>
  </div>
  
</template>

<style>

  body{
    background-color: #181818;
    margin: 0;
    padding: 0;
    color: #ffffff;
    font-size: 1.3em;
  }

  .main{
    display: flex;
    flex-direction: column;
    margin-top: 10%;
    width: 100%;
    justify-content: center;
    align-items: center;
    
  }

  .main button{

    margin-top: 10px;
    width: 10%;
    font-size: 1.1em;
    background-color: rgb(39, 133, 133);
  }

  .main ul{
    list-style-type: none;
    width: 50%;
    padding-inline-start: 0;
  }
  .main li{
    margin-bottom: 10px;
  }

  .main_item{
    margin-top: 10px;
    background-color:  #ffffff;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    color: #181818;
    width: 50%;
  }

  .main_item li button{
    width: 100%;
    display: flex;
    justify-content: center;
    font-size: 1.1em;
    
  }

  button:disabled{
    color: black;

  }
  button.correct{
    background-color: green;
    
  }
  button.incorrect{
    background-color: red;
    
  }
 
</style>

