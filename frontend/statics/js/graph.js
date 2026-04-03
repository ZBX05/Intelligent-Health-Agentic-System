function visualization(data){
    const width=window.innerWidth;
    const height=window.innerHeight;

    const color=d3.scaleOrdinal(d3.schemeCategory10);

    const links=data.links.map(d=>({...d}));
    const nodes=data.nodes.map(d=>({...d}));

    const simulation=d3.forceSimulation(nodes)
        .force("link",d3.forceLink(links).id(d=>d.id).distance(300))
        .force("charge",d3.forceManyBody().strength(-500))
        .force("x",d3.forceX())
        .force("y",d3.forceY());

    const svg=d3.select("#graph-container").append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox",[-width/2,-height/2,width,height])
        .attr("style","max-width: 100%; max-height: 100%; overflow: auto;");

    svg.append("defs").selectAll("marker")
        .data(["end"])
        .enter().append("marker")
        .attr("id",d=>d)
        .attr("viewBox","0 -5 10 10")
        .attr("refX",39)//箭头位置
        .attr("refY",-1)
        .attr("markerWidth",2.5)
        .attr("markerHeight",2.5)
        .attr("orient","auto")
        .append("path")
        .attr("d","M0,-5L10,0L0,5");

    const link=svg.append("g")
        .attr("stroke","#999")
        .attr("stroke-opacity",0.6)
        .selectAll("line")
        .data(links)
        .join("line")
        // .attr("stroke-width",Math.sqrt(2))
        .attr("stroke-width",4)
        .attr("marker-end","url(#end)");
        // .on("mouseover",()=>{
        //     link.append("title")
        //         .text(d=>d.name);
        // });
        // .on("mouseout",hideLinkName);

    const node=svg.append("g")
        .attr("stroke","#fff")
        .attr("stroke-width",1.5)
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r",30)//半径大小
        .attr("fill",d=>color(d.label));

    node.append("title")
        .text(d=>d.name);

    link.append("title")
        .text(d=>d.name);
    
    const nodeText=svg.selectAll(".node-text")
        .data(nodes)
        .enter().append("text")
        .attr("class","node-text")
        .attr("text-anchor","middle")
        .attr("dy","0.35em")
        .text(d=>d.name);

    const linkText=svg.selectAll(".link-text")
        .data(links)
        .enter().append("text")
        .attr("class","link-text")        
        .style("text-anchor","middle")
        .text(d=>d.name)
        .style("visibility","hidden");

    node.call(d3.drag()
        .on("start",dragstarted)
        .on("drag",dragged)
        .on("end",dragended));

    svg.call(d3.zoom()
        .extent([[0,0],[0,0,width,height]])
        .scaleExtent([0.5,100])
        .on("zoom",zoomed));

    function zoomed({transform}){
        let g=d3.selectAll('g');
        g.attr("transform",transform);
        nodeText.attr("transform",transform);
        linkText.attr("transform",transform);
    }

    simulation.on("tick",()=>{
        link
            .attr("x1",d=>d.source.x)
            .attr("y1",d=>d.source.y)
            .attr("x2",d=>d.target.x)
            .attr("y2",d=>d.target.y);
  
        node
            .attr("cx",d=>d.x)
            .attr("cy",d=>d.y);

        nodeText
            .attr("x",d=>d.x)
            .attr("y",d=>d.y);

        linkText
            .attr("x",d=>(d.source.x+d.target.x)/2)
            .attr("y",d=>(d.source.y+d.target.y)/2);
    });

    function dragstarted(event){
        if(!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx=event.subject.x;
            event.subject.fy=event.subject.y;
    }

    function dragged(event){
        event.subject.fx=event.x;
        event.subject.fy=event.y;
    }

    function dragended(event){
        if(!event.active) simulation.alphaTarget(0);
            event.subject.fx=null;
            event.subject.fy=null;
    }

    // function showLinkName(d){
    //     d3.select(this).attr("stroke","red");
    //     d3.select(this.parentNode).select("link-text").style("visibility", "visible");
    // }

    // function hideLinkName(d){
    //     d3.select(this).attr("stroke", "#999");
    //     d3.select(this.parentNode).select("link-text").style("visibility", "hidden");
    // }

    window.addEventListener("resize",()=>{
        const newWidth=window.innerWidth;
        const newHeight=window.innerHeight;

        simulation.force("center",d3.forceCenter(newWidth/2,newHeight/2));
        svg.attr("width",newWidth).attr("height",newHeight);
    });

    document.getElementById("btn-search").addEventListener("click",()=>{
        simulation.stop();
    });
}

function removeAllSVGs(){
    var svgElements=document.querySelectorAll('svg');
    svgElements.forEach(svg=>{
        svg.parentNode.removeChild(svg);
    });
}