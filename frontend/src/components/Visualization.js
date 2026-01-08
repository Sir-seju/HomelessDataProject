import React, { useEffect, useState } from "react";

const Visualization = () => {
  const [htmlContent, setHtmlContent] = useState("");

  useEffect(() => {
    fetch("http://homelessdatabackend-homeless-backend.us-east-1.elasticbeanstalk.com/visualize")
      .then((res) => res.text())
      .then((html) => setHtmlContent(html))
      .catch((err) => console.error("Error fetching visualization", err));
  }, []);

  return (
    <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
  );
};

export default Visualization;