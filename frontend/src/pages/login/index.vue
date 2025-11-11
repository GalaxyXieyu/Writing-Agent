<template>
	<div class="min-h-screen flex">
		<!-- 左侧品牌展示区 -->
		<div class="hidden lg:flex lg:flex-1 bg-gradient-to-br from-slate-900 to-slate-800 text-white p-12 flex-col relative">
			<!-- 左上角标题 -->
			<div>
				<span class="text-2xl font-bold tracking-tight">AI 智能写作助手</span>
			</div>
			
			<!-- 中间区域 Slogan -->
            <div class="flex-1 flex items-center justify-start">
				<div class="max-w-lg">
                  <p class="font-light leading-loose text-white/90 tracking-wide text-[clamp(28px,4vw,48px)]">
						智能内容创作<br/>
                      <span class="text-white/70 mt-4 block text-[clamp(22px,3vw,36px)]">让写作更高效</span>
					</p>
				</div>
			</div>
		</div>

		<!-- 右侧登录表单区 -->
		<div class="flex-1 flex items-center justify-center p-6 lg:p-12">
			<div class="w-full max-w-md">
				<div class="flex items-center justify-end mb-6">
					<button 
						@click="toggleMode" 
						class="text-sm text-muted-foreground hover:text-foreground"
					>
						{{ isRegisterMode ? '已有账号？登录' : '还没有账号？注册' }}
					</button>
				</div>

				<Card>
					<CardHeader>
                        <CardTitle class="text-2xl text-center">
                            {{ isRegisterMode ? (isInviteMode ? '邀请码注册' : '注册账户') : '登录账户' }}
                        </CardTitle>
						<CardDescription class="text-center">
							{{ isRegisterMode ? '在下方输入账号和密码以注册新账户' : '在下方输入您的账号和密码以登录账户' }}
						</CardDescription>
					</CardHeader>
					<CardContent>
                        <form @submit.prevent="isRegisterMode ? (isInviteMode ? handleInviteRegister() : handleRegister()) : handleLogin()" class="space-y-4">
							<div class="space-y-2">
								<label for="username" class="text-sm font-medium leading-none">账号</label>
								<Input
									id="username"
									v-model="loginForm.username"
									type="text"
									placeholder="请输入账号"
									required
								/>
							</div>
							<div class="space-y-2">
								<label for="password" class="text-sm font-medium leading-none">密码</label>
								<Input
									id="password"
									v-model="loginForm.password"
									type="password"
									placeholder="请输入密码"
									required
                                    @keyup.enter="isRegisterMode ? (isInviteMode ? handleInviteRegister() : handleRegister()) : handleLogin()"
								/>
							</div>
                            <div class="text-right -mt-2" v-if="isRegisterMode">
                                <button type="button" class="text-xs text-muted-foreground hover:text-foreground" @click="isInviteMode = !isInviteMode">
                                    {{ isInviteMode ? '使用普通注册' : '有邀请码？点此注册' }}
                                </button>
                            </div>
                            <div class="space-y-2" v-if="isRegisterMode && isInviteMode">
                                <label for="invite_code" class="text-sm font-medium leading-none">邀请码</label>
                                <Input
                                    id="invite_code"
                                    v-model="loginForm.invite_code"
                                    type="text"
                                    placeholder="请输入邀请码"
                                    required
                                />
                            </div>
							<Button
								type="submit"
								class="w-full"
								:disabled="loading"
							>
								{{ loading ? (isRegisterMode ? '注册中...' : '登录中...') : (isRegisterMode ? '注册' : '登录') }}
							</Button>
							<div class="relative">
								<div class="absolute inset-0 flex items-center">
									<Separator />
								</div>
								<div class="relative flex justify-center text-xs uppercase">
									<span class="bg-background px-2 text-muted-foreground">或继续使用</span>
								</div>
							</div>
							<Button
								variant="outline"
								type="button"
								class="w-full"
							>
								<svg class="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
									<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
								</svg>
								GitHub
							</Button>
							<p class="text-xs text-center text-muted-foreground">
								点击继续，即表示您同意我们的
								<a href="#" class="underline underline-offset-4 hover:text-primary">服务条款</a>
								和
								<a href="#" class="underline underline-offset-4 hover:text-primary">隐私政策</a>
							</p>
						</form>
					</CardContent>
				</Card>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store';
import { ElMessage } from 'element-plus';
import { solutionLogin, solutionRegister } from '@/service/api.solution';
import { registerWithInvite } from '@/service/api.invite';
import Card from '@/components/ui/Card.vue';
import CardHeader from '@/components/ui/CardHeader.vue';
import CardTitle from '@/components/ui/CardTitle.vue';
import CardDescription from '@/components/ui/CardDescription.vue';
import CardContent from '@/components/ui/CardContent.vue';
import Button from '@/components/ui/Button.vue';
import Input from '@/components/ui/Input.vue';
import Separator from '@/components/ui/Separator.vue';

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const isRegisterMode = ref(false);
const isInviteMode = ref(false);

const loginForm = reactive({
    username: '',
    password: '',
    invite_code: '',
});

const toggleMode = () => {
    isRegisterMode.value = !isRegisterMode.value;
    isInviteMode.value = false;
    // 切换模式时清空表单
    loginForm.username = '';
    loginForm.password = '';
    loginForm.invite_code = '';
};

const handleLogin = async () => {
	const username = loginForm.username?.trim();
	const password = loginForm.password?.trim();
	
	if (!username || !password) {
		ElMessage.warning('请输入账号和密码');
		return;
	}
	
	loading.value = true;
	try {
		const res = await solutionLogin({
			username,
			password,
		});
		
		if (res.code === 200 && res.data) {
			userStore.setToken(res.data.token);
			userStore.setProfile({
				name: res.data.name || res.data.username || '用户',
				user_id: res.data.user_id,
				username: res.data.username,
        is_admin: !!res.data.is_admin,
        parent_admin_id: res.data.parent_admin_id || null,
			});
			
			ElMessage.success(res.message || '登录成功');
			router.push('/web-solution-assistant');
		} else {
			ElMessage.error(res.message || '登录失败');
		}
	} catch (error) {
		ElMessage.error(error.message || '登录失败');
	} finally {
		loading.value = false;
	}
};

const handleInviteRegister = async () => {
    const username = loginForm.username?.trim();
    const password = loginForm.password?.trim();
    const invite_code = loginForm.invite_code?.trim();
    if (!username || !password || !invite_code) {
        ElMessage.warning('请输入账号、密码与邀请码');
        return;
    }
    loading.value = true;
    try {
        const res = await registerWithInvite({ username, password, invite_code });
        if (res.code === 200 && res.data) {
            userStore.setToken(res.data.token);
            userStore.setProfile({
                name: res.data.name || res.data.username || '用户',
                user_id: res.data.user_id,
                username: res.data.username,
                is_admin: !!res.data.is_admin,
                parent_admin_id: res.data.parent_admin_id || null,
            });
            ElMessage.success(res.message || '注册成功');
            router.push('/web-solution-assistant');
        } else {
            ElMessage.error(res.message || '注册失败');
        }
    } catch (error) {
        ElMessage.error(error.message || '注册失败');
    } finally {
        loading.value = false;
    }
};

const handleRegister = async () => {
	const username = loginForm.username?.trim();
	const password = loginForm.password?.trim();
	
	if (!username || !password) {
		ElMessage.warning('请输入账号和密码');
		return;
	}
	
	loading.value = true;
	try {
		const res = await solutionRegister({
			username,
			password,
		});
		
		if (res.code === 200 && res.data) {
			userStore.setToken(res.data.token);
			userStore.setProfile({
				name: res.data.name || res.data.username || '用户',
				user_id: res.data.user_id,
				username: res.data.username,
        is_admin: !!res.data.is_admin,
        parent_admin_id: res.data.parent_admin_id || null,
			});
			
			ElMessage.success(res.message || '注册成功');
			router.push('/web-solution-assistant');
		} else {
			ElMessage.error(res.message || '注册失败');
		}
	} catch (error) {
		ElMessage.error(error.message || '注册失败');
	} finally {
		loading.value = false;
	}
};
</script>

<style scoped lang="scss">
// 使用 Tailwind CSS，不需要额外样式
</style>

