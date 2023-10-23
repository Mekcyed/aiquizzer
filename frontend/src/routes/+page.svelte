<script>
// @ts-nocheck

	import { onMount } from 'svelte';
	import Button from './Button.svelte';
	let name = '';
	let questionQueue = [];
	let currentQuestionIndex = 0; 
	let currentQuestion = null;
	let topic = ""; 
	let selectedAnswer = "";
	let explanationText = "";
	let collection = "";
	let collections = [];
	let loading_question = false;
	let embeddings = ""; 
	let filename = "";
	let pageNumber = "";
	let criteria = "";
	let element = "";
	let questionQuantity = 2;
	let counter = 0;
	let counterInterval;

	onMount(async () => {
        await fetchCollections();
    });

	function startCounter() {
		counter = 0;  // Reset the counter
		counterInterval = setInterval(() => {
			counter++;
		}, 1000);  // Update the counter every 1 second (1000 milliseconds)
	}

	function stopCounter() {
		clearInterval(counterInterval);
	}

	async function fetchCollections() {
		try {
			const result = await fetch('http://localhost:5000/api/get/collections');
			const data = await result.json();
			
			// Check if the data contains a 'collections' object and then if the expected sub-structures are present
			if (data?.collections && 
				Object.values(data.collections).every(collection => collection.filenames)) {
				collections = data.collections;
				collection = Object.keys(collections)[0];
			} else {
				alert("Invalid API response.");
			} 
		} catch (error) {
			console.error("Error fetching collections:", error);
		}
	}

	// This function will be called when the button is clicked
	async function fetchData() {
		loading_question = true;
		startCounter();
		questionQueue = [];
		currentQuestionIndex = 0;
		currentQuestion = null;
		explanationText = "";
		selectedAnswer = "";
		if (topic != "") {
			criteria = "topic";
			element = topic;
		} else if (filename != "" && pageNumber != "") {
			criteria = "filename";
			element = filename + "_" + pageNumber;
		} else {
			alert("Please enter a topic or filename and page number.");
		}
		try {
			const result = await fetch(`http://localhost:5000/api/get/question/${questionQuantity}/${collection}/${criteria}/${element}`);
			const data = await result.json();
			if (data?.response && data?.response?.embeddings && data?.response?.questions) {
				console.log(data.response);
				questionQueue = data?.response?.questions;
				console.log(questionQueue);
				embeddings = data.response.embeddings;
				console.log(embeddings);
				loadNextQuestion();
			} else {
				if (data?.error){
					alert(data.error);
				} else {
					alert("Invalid API response.");
				}
			}
		} catch (error) {
			console.error("Error fetching data:", error);
		} finally {
			loading_question = false;
			stopCounter();
		}
	}

	function loadNextQuestion() {
		if (currentQuestionIndex < questionQueue.length) {
			explanationText = ""; 
			selectedAnswer = "";
			currentQuestion = questionQueue[currentQuestionIndex];  
        	currentQuestionIndex++; 
		} else {
			alert("No more questions.");
		}
	}

	function checkAnswer() {
		if (selectedAnswer == currentQuestion.answer) {
			explanationText = "Correct! " + currentQuestion.explanation;
		} else {
			explanationText = "Incorrect! " + currentQuestion.explanation;
		}
	}

	function showNextQuestion() {
		loadNextQuestion();  
	}

	function showPreviousQuestion() {
		if (currentQuestionIndex > 1) {
			currentQuestionIndex -= 2; 
			loadNextQuestion(); 
		} else {
			alert("No previous questions.");
		}
	}
</script>

<div class="container">
    <h1>AiQuizzer</h1>
    <h1>Let's test your uni knowledge!</h1>
    <div class="group">
        <p>Choose a collection:</p>
        <select bind:value={collection}>
            {#each Object.keys(collections) as collectionName}
                <option value={collectionName}>{collectionName}</option>
            {/each}
        </select>
        <p>Enter a filename:</p>
        <select bind:value={filename}>
            {#if collections[collection]}
                {#each collections[collection].filenames as filenameSelect}
                    <option value={filenameSelect}>{filenameSelect} </option>
                {/each}
            {/if}
        </select>
        {#if filename}
        <p>And a page number:</p>
        <input bind:value={pageNumber} placeholder=1 />
        {/if}
        <p>Or enter a topic:</p>
        <input bind:value={topic} placeholder="Enter topic" />
		<p>Enter the number of questions you want:</p>
		<input bind:value={questionQuantity} placeholder=2 />
    </div>

</div>


<div class="container">
	<Button handleClick={fetchData}>
		Fetch Question
	</Button>
	{#if loading_question}
		<div class="loader"></div>
		<div class="counter">Time elapsed: {counter} seconds</div>
	{/if}	
	{#if currentQuestion}
	<div class="container question-container">
		<h2>{currentQuestion.query}</h2>
		{#each currentQuestion.choices as choice, index}
			<label class="choice-label">
				<input type="radio" bind:group={selectedAnswer} value={index}>
				{choice}
			</label>
		{/each}
		<Button handleClick={checkAnswer}>
			Submit
		</Button>
		<p class="explanation">{explanationText}</p>
		<Button handleClick={showPreviousQuestion}>
			Previous Question
		</Button>
		<Button handleClick={showNextQuestion}>
			Next Question
		</Button>
		<p>	
			Used Script {embeddings.metadatas[0].document} on Page {embeddings.metadatas[0].page}.<br />
			Used Embeddings: {embeddings.documents[0]} 
		</p>
	</div>
	{/if}


	<Button handleClick={() => document.body.classList.toggle('dark-mode')}>
		Toggle Dark Mode
	</Button>
</div>


<style>
	@font-face {
		font-family: 'Atkison Hyperlegible';
		src: local(''), url('/fonts/Atkinson-Hyperlegible-Regular-102a.woff2') format('woff2');
		font-weight: normal;
		font-style: normal;
	}
	.loader {
		border: 16px solid #f3f3f3;  /* Light grey */
		border-top: 16px solid #3498db; /* Blue */
		border-radius: 50%;
		width: 50px;
		height: 50px;
		animation: spin 2s linear infinite;
	}
	.counter {
        margin-top: 10px;
        font-size: 14px;
    }
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
    .container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
	  margin: 1rem 0;
    }
	.group {
		display: flex;
      	flex-direction: column;
        margin-bottom: 1rem;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 8px;
		align-items: center;
		justify-content: center;
    }
	:global(body) {
		background-color: #f2eee2;
		color: #0084f6;
		transition: background-color 0.3s;
		font-family: 'Atkison Hyperlegible', sans-serif; 
	}
	:global(body.dark-mode) {
		background-color: #000000;
		color: #ffff;
	}
	.question-container h2 {
		margin: 1rem 0;
	}
	.choice-label {
		margin-bottom: 0.5rem;
		display: block; 
	}
</style>
