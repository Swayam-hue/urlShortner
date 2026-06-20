import http from 'k6/http';
import { Counter } from 'k6/metrics';

const errors = new Counter('errors');

export default function () {
    const res = http.post(
        'https://urlshortner.fastapicloud.dev/hash',
        JSON.stringify({
            longURL: 'https://grafana.com/docs/k6/latest/get-started/write-your-first-test/'
        }),
        {
            headers: {
                'Content-Type': 'application/json'
            }
        }
    );
    if (res.status !== 200) {
        console.log(`Status: ${res.status}`);
        console.log(res.body);
        errors.add(1);
}
}