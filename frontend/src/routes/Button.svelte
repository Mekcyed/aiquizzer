<script>
	export let handleClick = null;
</script>

<button on:click={handleClick}>
    <slot/>
</button>

<style>
    button {
        background-color: #f76027;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        text-transform: uppercase;
        margin: 0.5rem 0;
    }
    :global(body.dark-mode) button {
        background-color: #0084f6;
        color: white;
    }
</style>
