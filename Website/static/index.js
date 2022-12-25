function likePost(postId){
    const likesCount = document.getElementById(`likes-count-${postId}`)
    const likeButton = document.getElementById(`like-button-${postId}`)

    fetch(`/like-post-${postId}`,
    {method: "POST"})
    .then((res) => res.json())
    .then((data) => {
        likesCount.innerHTML = data["likes_count"];

        if (data["liked"] === true){
            likeButton.className = "fas fa-heart";
        } else{
            likeButton.className = "far fa-heart";
        }
    })
    .catch((error) => {
    console.error(error);
    });
    ;
}